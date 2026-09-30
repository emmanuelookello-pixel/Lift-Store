"""Email verification and recovery. Tokens are random, hashed, expiring and one-use."""
import os,secrets,hashlib,smtplib,ssl
from datetime import datetime,timedelta
from email.message import EmailMessage
from urllib.parse import urlparse
from flask import request,session,render_template,redirect,url_for,flash,abort
from werkzeug.security import generate_password_hash

def install(s):
 app,db,User=s.app,s.db,s.User
 class AccountSecurity(db.Model):
  user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
  version=db.Column(db.Integer,default=0,nullable=False)
  verified_email=db.Column(db.String(150))
 class AccountToken(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
  digest=db.Column(db.String(64),unique=True,nullable=False)
  purpose=db.Column(db.String(20),nullable=False)
  email=db.Column(db.String(150),nullable=False)
  expires=db.Column(db.DateTime,nullable=False)
  used=db.Column(db.Boolean,default=False,nullable=False)
 class AccountThrottle(db.Model):
  key=db.Column(db.String(64),primary_key=True)
  started=db.Column(db.DateTime,nullable=False)
  attempts=db.Column(db.Integer,nullable=False,default=0)
 def ready():
  origin=os.environ.get('STORE_PUBLIC_URL','');parsed=urlparse(origin)
  return bool(os.environ.get('SMTP_HOST') and os.environ.get('SMTP_FROM') and (not os.environ.get('SMTP_USERNAME') or os.environ.get('SMTP_PASSWORD')) and parsed.scheme=='https' and parsed.hostname and not parsed.username and not parsed.query and not parsed.fragment)
 def state(user):
  return db.session.get(AccountSecurity,user.id)
 def stamp(user):
  row=state(user);session['auth_version']=row.version if row else 0
 def guard():
  if request.path=='/admin' or request.path.startswith('/admin/'):return
  uid=session.get('user_id')
  if uid:
   user=db.session.get(User,uid);row=db.session.get(AccountSecurity,uid)
   if not user or user.active is False or session.get('auth_version',0)!=(row.version if row else 0):
    for key in ('user_id','user_name','auth_version','cart','guest_order_ids'):session.pop(key,None)
 app.before_request_funcs.setdefault(None,[]).insert(0,guard)
 def limited(identity):
  now=datetime.utcnow();blocked=False
  for kind,value,maximum in [('ip',request.remote_addr or '',20),('identity',identity.lower(),3)]:
   key=hashlib.sha256((kind+':'+value).encode()).hexdigest();row=db.session.get(AccountThrottle,key)
   if not row:row=AccountThrottle(key=key,started=now,attempts=0);db.session.add(row)
   if row.started<now-timedelta(minutes=15):row.started=now;row.attempts=0
   row.attempts+=1;blocked=blocked or row.attempts>maximum
  db.session.commit();return blocked
 def send(user,purpose):
  raw=secrets.token_urlsafe(32)
  record=AccountToken(user_id=user.id,digest=hashlib.sha256(raw.encode()).hexdigest(),purpose=purpose,email=user.email,expires=datetime.utcnow()+timedelta(minutes=30))
  db.session.add(record);db.session.commit()
  endpoint='reset_account_password' if purpose=='reset' else 'verify_account_email'
  link=os.environ['STORE_PUBLIC_URL'].rstrip('/')+url_for(endpoint,token=raw)
  message=EmailMessage();message['From']=os.environ['SMTP_FROM'];message['To']=user.email
  message['Subject']='Reset your Lift Store password' if purpose=='reset' else 'Verify your Lift Store email'
  message.set_content(('Reset your password' if purpose=='reset' else 'Verify your email')+' using this link within 30 minutes:\n\n'+link+'\n\nIf you did not request this, ignore this email.')
  try:
   sender=app.config.get('ACCOUNT_MAIL_SENDER') if app.testing else None
   if sender:sender(message)
   else:
    with smtplib.SMTP(os.environ['SMTP_HOST'],int(os.environ.get('SMTP_PORT','587')),timeout=10) as smtp:
     smtp.starttls(context=ssl.create_default_context())
     if os.environ.get('SMTP_USERNAME'):smtp.login(os.environ['SMTP_USERNAME'],os.environ.get('SMTP_PASSWORD',''))
     smtp.send_message(message)
   return True
  except Exception:
   record.used=True;db.session.commit();app.logger.warning('Account email delivery failed.');return False
 def valid(raw,purpose):
  if len(raw)>100:return None
  token=AccountToken.query.filter_by(digest=hashlib.sha256(raw.encode()).hexdigest(),purpose=purpose,used=False).first()
  if not token or token.expires<datetime.utcnow():return None
  user=db.session.get(User,token.user_id)
  return token if user and user.active is not False and user.email==token.email else None
 @app.context_processor
 def security_context():
  customer=s.current_customer();row=state(customer) if customer else None
  return dict(account_email_ready=ready(),email_verified=bool(customer and row and row.verified_email==customer.email))
 @app.route('/account/recovery',methods=['GET','POST'])
 def account_recovery():
  if request.method=='POST':
   if not ready():flash('Email recovery is not available yet. Please contact the store.','warning')
   else:
    identity=request.form.get('email','').strip().lower()[:150]
    if not limited(identity):
     user=User.query.filter(db.func.lower(User.email)==identity).first()
     if user and user.active is not False and not user.email.endswith('@accounts.invalid'):send(user,'reset')
    flash('If an eligible account matches, a reset link will be sent. Check your inbox and spam folder.','success')
   return redirect(url_for('account_recovery'))
  return render_template('account_security.html',mode='request',valid=True)
 @app.route('/account/reset/<token>',methods=['GET','POST'])
 def reset_account_password(token):
  record=valid(token,'reset')
  if request.method=='POST' and record:
   password=request.form.get('password','')
   if not 8<=len(password)<=128 or password!=request.form.get('confirm_password'):
    flash('Use matching passwords between 8 and 128 characters.','danger')
   else:
    changed=db.session.execute(db.update(AccountToken).where(AccountToken.id==record.id,AccountToken.used.is_(False)).values(used=True))
    if changed.rowcount!=1:db.session.rollback();abort(400)
    user=db.session.get(User,record.user_id);user.password=generate_password_hash(password)
    row=state(user) or AccountSecurity(user_id=user.id,version=0)
    row.version+=1;db.session.add(row)
    AccountToken.query.filter_by(user_id=user.id,purpose='reset',used=False).update({'used':True})
    db.session.commit()
    if session.get('user_id')==user.id:
     for key in ('user_id','user_name','auth_version','cart','guest_order_ids'):session.pop(key,None)
    flash('Password updated. Sign in with your new password.','success');return redirect(url_for('login'))
  return render_template('account_security.html',mode='reset',valid=bool(record))
 @app.route('/account/verification',methods=['POST'])
 def request_email_verification():
  user=s.current_customer()
  if not user:return redirect(url_for('login'))
  if not ready():flash('Email verification is not available yet.','warning')
  elif user.email.endswith('@accounts.invalid'):flash('Add an email address to your profile first.','warning')
  elif limited(user.email):flash('Please wait 15 minutes before requesting another link.','warning')
  elif send(user,'verify'):flash('Check your email for a verification link.','success')
  else:flash('The email could not be sent. Please try again later.','warning')
  return redirect(url_for('customer_profile'))
 @app.route('/account/verify/<token>',methods=['GET','POST'])
 def verify_account_email(token):
  record=valid(token,'verify')
  if request.method=='POST' and record:
   changed=db.session.execute(db.update(AccountToken).where(AccountToken.id==record.id,AccountToken.used.is_(False)).values(used=True))
   if changed.rowcount!=1:db.session.rollback();abort(400)
   user=db.session.get(User,record.user_id);row=state(user) or AccountSecurity(user_id=user.id,version=0)
   row.verified_email=record.email;db.session.add(row);db.session.commit()
   flash('Email address verified.','success');return redirect(url_for('customer_profile'))
  return render_template('account_security.html',mode='verify',valid=bool(record))
 @app.after_request
 def private_security_pages(response):
  if request.endpoint in ('reset_account_password','verify_account_email','account_recovery'):
   response.headers['Cache-Control']='no-store';response.headers['Referrer-Policy']='no-referrer'
  return response
 @app.route('/admin/account-security')
 @s.admin_required
 def account_security_admin():
  return render_template('admin_account_security.html',ready=ready())
 @app.cli.command('init-account-security')
 def initialize():
  for model in (AccountSecurity,AccountToken,AccountThrottle):model.__table__.create(db.engine,checkfirst=True)
 return stamp,(AccountSecurity,AccountToken,AccountThrottle)
