"""Administrator TOTP enrollment, recovery and route-level staff permissions."""
import base64,hashlib,hmac,os,secrets,struct,time
from pathlib import Path
from datetime import datetime,timedelta
from flask import request,session,redirect,url_for,render_template,flash,abort
from werkzeug.security import check_password_hash,generate_password_hash

def totp(secret,counter,digits=6):
 digest=hmac.new(base64.b32decode(secret),struct.pack('>Q',counter),hashlib.sha1).digest()
 offset=digest[-1]&15
 return str((struct.unpack('>I',digest[offset:offset+4])[0]&0x7fffffff)%(10**digits)).zfill(digits)

def install(s):
 app,db,Admin=s.app,s.db,s.Admin
 class AdminAccess(db.Model):
  admin_id=db.Column(db.Integer,db.ForeignKey('admin.id'),primary_key=True)
  role=db.Column(db.String(20),nullable=False,default='support')
  secret=db.Column(db.Text)
  pending=db.Column(db.Text)
  pending_expires=db.Column(db.DateTime)
  last_counter=db.Column(db.BigInteger,nullable=False,default=-1)
  version=db.Column(db.Integer,nullable=False,default=0)
  failures=db.Column(db.Integer,nullable=False,default=0)
  locked_until=db.Column(db.DateTime)
 class AdminRecovery(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  admin_id=db.Column(db.Integer,db.ForeignKey('admin.id'),nullable=False,index=True)
  digest=db.Column(db.String(64),nullable=False,unique=True)
 class AdminLoginLimit(db.Model):
  key=db.Column(db.String(64),primary_key=True)
  started=db.Column(db.DateTime,nullable=False)
  attempts=db.Column(db.Integer,nullable=False,default=0)
 roles={'owner':'Owner','manager':'Store manager','inventory':'Inventory staff','support':'Support staff'}
 common={'admin_profile','admin_profile_photo','admin_logout','admin_security'}
 catalogue={'admin_products','admin_add_product','admin_edit_product','admin_categories','admin_add_category','admin_edit_category','admin_toggle_category','admin_brands','admin_add_brand','admin_edit_brand','admin_inventory','admin_update_stock'}
 sales={'admin_orders','admin_order_detail','admin_update_order_status','admin_customers','admin_customer_detail','admin_support','admin_reviews','admin_review_visibility'}
 permissions={'inventory':catalogue,'support':{'admin_orders','admin_order_detail','admin_support','admin_reviews'},'manager':catalogue|sales|{'admin_dashboard','admin_coupons','admin_coupon_form','admin_coupon_active','admin_delivery_areas','admin_delivery_area_form','admin_delivery_area_active'}}
 for staff_role in ('manager','support'):
  permissions[staff_role].update({'admin_chat','admin_chat_thread','admin_chat_messages','admin_chat_inbox','admin_chat_attachment','admin_chat_alerts','admin_chat_customer_photo'})
 def access(admin):return db.session.get(AdminAccess,admin.id) if admin else None
 def current():return db.session.get(Admin,session.get('admin_id')) if session.get('admin_logged_in') else None
 def can(endpoint):
  admin=current();row=access(admin)
  return bool(admin and admin.active and row and (row.role=='owner' or endpoint in common or endpoint in permissions.get(row.role,set())))
 def destination(row):return {'inventory':'admin_inventory','support':'admin_orders'}.get(row.role,'admin_dashboard')
 def cipher():
  from cryptography.fernet import Fernet
  key=os.environ.get('ADMIN_MFA_KEY')
  if key:return Fernet(key.encode())
  path=Path(app.instance_path)/'admin-mfa.key'
  if not path.exists():
   if AdminAccess.query.filter(AdminAccess.secret.isnot(None)).first():raise RuntimeError('Restore the admin MFA encryption key before continuing.')
   path.parent.mkdir(parents=True,exist_ok=True)
   try:
    with path.open('xb') as output:output.write(Fernet.generate_key())
   except FileExistsError:pass
  return Fernet(path.read_bytes())
 def consume(row,code,allow_recovery=True):
  now=datetime.utcnow()
  if row.locked_until and row.locked_until>now:return False
  if row.locked_until:row.locked_until=None;row.failures=0
  code=code.strip().replace(' ','')
  matched=None
  if row.secret and len(code)==6 and code.isdigit():
   secret=cipher().decrypt(row.secret.encode()).decode();counter=int(time.time())//30
   matched=next((step for step in range(counter-1,counter+2) if step>row.last_counter and hmac.compare_digest(totp(secret,step),code)),None)
  if matched is not None:
   changed=db.session.execute(db.update(AdminAccess).where(AdminAccess.admin_id==row.admin_id,AdminAccess.last_counter<matched).values(last_counter=matched,failures=0,locked_until=None))
   if changed.rowcount==1:db.session.commit();return True
  if allow_recovery:
   digest=hashlib.sha256(code.upper().encode()).hexdigest()
   changed=db.session.execute(db.delete(AdminRecovery).where(AdminRecovery.admin_id==row.admin_id,AdminRecovery.digest==digest))
   if changed.rowcount==1:row.failures=0;row.locked_until=None;db.session.commit();return True
  row.failures+=1
  if row.failures>=5:row.locked_until=now+timedelta(minutes=5)
  db.session.commit();return False
 def login_limited():
  key=hashlib.sha256((request.remote_addr or '').encode()).hexdigest();now=datetime.utcnow();row=db.session.get(AdminLoginLimit,key)
  if not row:row=AdminLoginLimit(key=key,started=now,attempts=0);db.session.add(row)
  if row.started<now-timedelta(minutes=5):row.started=now;row.attempts=0
  row.attempts+=1;db.session.commit();return row.attempts>15
 def guard():
  if not (request.path=='/admin' or request.path.startswith('/admin/')):return
  if request.endpoint=='admin_login':
   if request.method=='POST' and login_limited():return render_template('admin_access_denied.html',message='Too many sign-in attempts. Please wait five minutes.'),429
   return
  if request.endpoint in ('admin_mfa_challenge','admin_logout'):return
  admin=current();row=access(admin)
  if not admin or not admin.active or not row or session.get('admin_version',0)!=row.version or (row.secret and not session.get('admin_mfa_verified')):
   session.clear();return redirect(url_for('admin_login'))
  if not can(request.endpoint):
   if request.endpoint=='admin_dashboard':return redirect(url_for(destination(row)))
   return render_template('admin_access_denied.html',message='Your staff role does not have access to this page.'),403
 app.before_request_funcs.setdefault(None,[]).insert(0,guard)
 original_login=app.view_functions['admin_login']
 def secure_login():
  response=original_login()
  if request.method=='POST' and session.get('admin_logged_in'):
   admin=current();row=access(admin)
   if not row:session.clear();abort(403)
   if row.secret:
    session.clear();session['mfa_pending']=admin.id;session['mfa_started']=time.time()
    return redirect(url_for('admin_mfa_challenge'))
   session['admin_version']=row.version
   return redirect(url_for(destination(row)))
  return response
 app.view_functions['admin_login']=secure_login
 @app.context_processor
 def context():return {'admin_can':can,'admin_roles':roles}
 @app.route('/admin/two-factor',methods=['GET','POST'])
 def admin_mfa_challenge():
  admin=db.session.get(Admin,session.get('mfa_pending')) if session.get('mfa_pending') else None
  if not admin or not admin.active or time.time()-session.get('mfa_started',0)>300:
   session.clear();return redirect(url_for('admin_login'))
  row=access(admin)
  if not row or not row.secret:session.clear();return redirect(url_for('admin_login'))
  if request.method=='POST':
   try:accepted=consume(row,request.form.get('code',''))
   except Exception:accepted=False;flash('Authenticator verification is unavailable. Contact the store owner.','danger')
   if accepted:
    session.clear();session.update(admin_logged_in=True,admin_id=admin.id,admin_email=admin.email,admin_version=row.version,admin_mfa_verified=True)
    return redirect(url_for(destination(row)))
   flash('Invalid or already-used code. After five failed attempts, wait five minutes.','danger')
  return render_template('admin_mfa_challenge.html')
 @app.route('/admin/security',methods=['GET','POST'])
 def admin_security():
  admin=current();row=access(admin);setup_secret=None;codes=[]
  if request.method=='POST':
   action=request.form.get('action')
   if not check_password_hash(admin.password,request.form.get('password','')):flash('Enter your current administrator password.','danger')
   else:
    try:
     if action=='start' and not row.secret:
      setup_secret=base64.b32encode(secrets.token_bytes(20)).decode();row.pending=cipher().encrypt(setup_secret.encode()).decode();row.pending_expires=datetime.utcnow()+timedelta(minutes=10);db.session.commit()
     elif action=='confirm' and row.pending and row.pending_expires>datetime.utcnow() and not row.secret:
      secret=cipher().decrypt(row.pending.encode()).decode();counter=int(time.time())//30;code=request.form.get('code','').strip()
      if row.locked_until and row.locked_until>datetime.utcnow():flash('Please wait five minutes before trying again.','danger')
      elif any(hmac.compare_digest(totp(secret,step),code) for step in range(counter-1,counter+2)):
       row.secret=row.pending;row.pending=None;row.pending_expires=None;row.last_counter=next(step for step in range(counter-1,counter+2) if hmac.compare_digest(totp(secret,step),code));row.version+=1;row.failures=0;row.locked_until=None
       AdminRecovery.query.filter_by(admin_id=admin.id).delete()
       codes=[secrets.token_hex(6).upper() for _ in range(8)]
       for recovery in codes:db.session.add(AdminRecovery(admin_id=admin.id,digest=hashlib.sha256(recovery.encode()).hexdigest()))
       db.session.commit();session['admin_version']=row.version;session['admin_mfa_verified']=True;flash('Two-factor authentication enabled. Save your recovery codes now.','success')
      else:
       row.failures+=1
       if row.failures>=5:row.locked_until=datetime.utcnow()+timedelta(minutes=5);row.failures=0
       db.session.commit();flash('The code did not match. Try the current code from your app.','danger')
     elif action=='disable' and row.secret:
      if consume(row,request.form.get('code','')):
       row.secret=None;row.pending=None;row.version+=1;AdminRecovery.query.filter_by(admin_id=admin.id).delete();db.session.commit();session['admin_version']=row.version;flash('Two-factor authentication disabled.','warning')
      else:flash('Enter a valid authenticator or recovery code.','danger')
    except Exception:
     db.session.rollback();flash('Setup could not be completed. Check the server encryption configuration.','danger')
  return render_template('admin_security.html',enabled=bool(row.secret),pending=bool(row.pending and row.pending_expires>datetime.utcnow()),setup_secret=setup_secret,codes=codes)
 @app.route('/admin/staff',methods=['GET','POST'])
 def admin_staff():
  admin=current()
  if request.method=='POST':
   if not check_password_hash(admin.password,request.form.get('current_password','')):flash('Confirm your administrator password.','danger')
   else:
    target=db.get_or_404(Admin,request.form.get('admin_id',type=int));row=access(target);role=request.form.get('role');active=request.form.get('active')=='1'
    if role not in roles or not row:abort(400)
    if target.id==admin.id and (role!='owner' or not active):flash('You cannot remove your own owner access.','danger')
    else:
     row.role=role;row.version+=1;target.active=active;db.session.commit();flash('Staff permissions updated. The staff member must sign in again.','success')
   return redirect(url_for('admin_staff'))
  members=[(admin,access(admin)) for admin in Admin.query.order_by(Admin.id).all()]
  return render_template('admin_staff.html',members=members)
 @app.route('/admin/staff/new',methods=['POST'])
 def admin_staff_new():
  owner=current()
  if not check_password_hash(owner.password,request.form.get('current_password','')):
   flash('Confirm your administrator password.','danger');return redirect(url_for('admin_staff'))
  name=request.form.get('name','').strip();email=request.form.get('email','').strip().lower();password=request.form.get('password','');role=request.form.get('role')
  import re
  if not name or len(name)>100 or len(email)>150 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or not 12<=len(password)<=128 or role not in ('manager','inventory','support'):
   flash('Enter valid staff details and a password of 12 to 128 characters.','danger');return redirect(url_for('admin_staff'))
  if Admin.query.filter(db.func.lower(Admin.email)==email).first():
   flash('This administrator email is already registered.','danger');return redirect(url_for('admin_staff'))
  try:
   member=Admin(name=name,email=email,password=generate_password_hash(password),active=True);db.session.add(member);db.session.flush();db.session.add(AdminAccess(admin_id=member.id,role=role));db.session.commit();flash('Staff account created. Share sign-in details privately.','success')
  except Exception:db.session.rollback();flash('The staff account could not be created.','danger')
  return redirect(url_for('admin_staff'))
 @app.after_request
 def no_cache(response):
  if request.path.startswith('/admin/') or request.path=='/admin':response.headers['Cache-Control']='no-store'
  return response
 @app.cli.command('init-admin-security')
 def initialize():
  for model in (AdminAccess,AdminRecovery,AdminLoginLimit):model.__table__.create(db.engine,checkfirst=True)
  first=Admin.query.filter_by(active=True).order_by(Admin.id).first()
  for admin in Admin.query:
   if not access(admin):db.session.add(AdminAccess(admin_id=admin.id,role='owner' if first and admin.id==first.id else 'manager'))
  db.session.commit()
 return (AdminAccess,AdminRecovery,AdminLoginLimit)
