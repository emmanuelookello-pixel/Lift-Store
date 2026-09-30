"""Private customer/staff conversations with incremental polling."""
from datetime import datetime,timedelta
from urllib.parse import urlencode
import re,io
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import send_file
from flask import request,session,redirect,url_for,render_template,jsonify,abort
from sqlalchemy.exc import IntegrityError

def install(s):
 app,db=s.app,s.db
 class ChatThread(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  user_id=db.Column(db.Integer,db.ForeignKey('user.id'),unique=True,nullable=False)
  updated_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False,index=True)
  user=db.relationship(s.User)
 class ChatMessage(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  thread_id=db.Column(db.Integer,db.ForeignKey('chat_thread.id'),nullable=False,index=True)
  sender=db.Column(db.String(10),nullable=False)
  admin_id=db.Column(db.Integer,db.ForeignKey('admin.id'))
  text=db.Column(db.String(2000),nullable=False)
  nonce=db.Column(db.String(64),nullable=False)
  created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
  __table_args__=(db.UniqueConstraint('thread_id','sender','nonce'),)
 class ChatAttachment(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  message_id=db.Column(db.Integer,db.ForeignKey('chat_message.id'),nullable=False,unique=True)
  filename=db.Column(db.String(200),nullable=False)
  mime=db.Column(db.String(50),nullable=False)
  data=db.Column(db.LargeBinary,nullable=False)
 class ChatRead(db.Model):
  reader=db.Column(db.String(40),primary_key=True)
  thread_id=db.Column(db.Integer,db.ForeignKey('chat_thread.id'),primary_key=True)
  last_id=db.Column(db.Integer,nullable=False,default=0)
 @app.before_request
 def upload_limit():
  if request.endpoint in ('customer_chat_messages','admin_chat_messages'):request.max_content_length=6*1024*1024
 app.before_request_funcs[None].remove(upload_limit)
 app.before_request_funcs[None].insert(0,upload_limit)
 def read_attachment(upload):
  if not upload or not upload.filename:return None
  data=upload.read(5*1024*1024+1)
  if not data or len(data)>5*1024*1024:raise ValueError('Choose a non-empty file up to 5 MB.')
  filename=secure_filename(upload.filename)[:200] or 'attachment';extension=Path(filename).suffix.lower()
  mime=None
  if extension in ('.jpg','.jpeg') and data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9'):mime='image/jpeg'
  elif extension=='.png' and data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)>=45:mime='image/png'
  elif extension=='.webp' and data[:4]==b'RIFF' and data[8:12]==b'WEBP':mime='image/webp'
  elif extension=='.webm' and data.startswith(b'\x1a\x45\xdf\xa3') and b'webm' in data[:256]:mime='audio/webm'
  elif extension in ('.ogg','.oga') and data.startswith(b'OggS'):mime='audio/ogg'
  elif extension in ('.m4a','.mp4') and len(data)>12 and data[4:8]==b'ftyp':mime='audio/mp4'
  elif extension=='.wav' and data[:4]==b'RIFF' and data[8:12]==b'WAVE':mime='audio/wav'
  elif extension=='.mp3' and (data.startswith(b'ID3') or (len(data)>2 and data[0]==255 and data[1]&224==224)):mime='audio/mpeg'
  elif extension=='.pdf' and data.startswith(b'%PDF-'):mime='application/pdf'
  elif extension=='.txt':
   try:data.decode('utf-8')
   except UnicodeDecodeError:raise ValueError('Text files must use UTF-8 encoding.')
   if b'\x00' in data:raise ValueError('Invalid text file.')
   mime='text/plain'
  if not mime:raise ValueError('Choose a supported picture, audio, PDF or UTF-8 text file.')
  return dict(filename=filename,mime=mime,data=data)
 def message_json(message,sender):
  attachment=ChatAttachment.query.filter_by(message_id=message.id).first()
  result={'id':message.id,'sender':message.sender,'text':message.text,'time':message.created_at.isoformat()+'Z'}
  if attachment:
   result['attachment']={'name':attachment.filename,'size':len(attachment.data),'image':attachment.mime.startswith('image/'),'audio':attachment.mime.startswith('audio/'),'url':url_for('admin_chat_attachment' if sender=='admin' else 'customer_chat_attachment',attachment_id=attachment.id)}
  if message.sender=='customer':
   thread=db.session.get(ChatThread,message.thread_id)
   result['name']=thread.user.name
   result['avatar']=customer_avatar(thread,sender=='admin')
  return result
 def customer_avatar(thread,admin=True):
  path=s.customer_photo_path(thread.user)
  if not path.is_file():return None
  return url_for('admin_chat_customer_photo',thread_id=thread.id,v=path.stat().st_mtime_ns) if admin else url_for('customer_profile_photo',v=path.stat().st_mtime_ns)
 @app.route('/admin/chat/<int:thread_id>/customer-photo')
 def admin_chat_customer_photo(thread_id):
  thread=db.get_or_404(ChatThread,thread_id);path=s.customer_photo_path(thread.user)
  if not path.is_file():abort(404)
  response=send_file(io.BytesIO(path.read_bytes()),mimetype='image/png')
  response.headers['Cache-Control']='private, no-store';response.headers['X-Content-Type-Options']='nosniff';return response
 def whatsapp():
  settings=s.StoreSetting.query.first();number=re.sub(r'[^0-9]','',settings.whatsapp or '') if settings else ''
  if not 8<=len(number)<=15:return None
  return 'https://wa.me/'+number+'?'+urlencode({'text':'Hello, I would like help with shopping at '+(settings.store_name or 'Lift Store')+'.'})
 @app.context_processor
 def context():return {'whatsapp_chat_url':whatsapp(),'chat_customer_avatar':customer_avatar}
 def customer_thread(create=False):
  user=s.current_customer()
  if not user:return None
  thread=ChatThread.query.filter_by(user_id=user.id).first()
  if not thread and create:
   thread=ChatThread(user_id=user.id);db.session.add(thread)
   try:db.session.commit()
   except IntegrityError:db.session.rollback();thread=ChatThread.query.filter_by(user_id=user.id).first()
  return thread
 def conversation(thread,sender):
  if request.method=='POST':
   data=request.form if request.mimetype=='multipart/form-data' else (request.get_json(silent=True) or {});body=data.get('text','');nonce=data.get('nonce','')
   upload=request.files.get('attachment')
   if not isinstance(body,str) or len(body.strip())>2000 or (not body.strip() and not (upload and upload.filename)) or not isinstance(nonce,str) or not re.fullmatch(r'[a-zA-Z0-9-]{16,64}',nonce):return jsonify(error='Enter a message of 1 to 2,000 characters.'),400
   previous=ChatMessage.query.filter_by(thread_id=thread.id,sender=sender,nonce=nonce).first()
   if previous:return jsonify(id=previous.id),200
   try:attachment=read_attachment(upload)
   except ValueError as error:return jsonify(error=str(error)),400
   recent=ChatMessage.query.filter_by(thread_id=thread.id,sender=sender).filter(ChatMessage.created_at>datetime.utcnow()-timedelta(minutes=1)).count()
   if recent>=20:return jsonify(error='Please wait a minute before sending more messages.'),429
   message=ChatMessage(thread_id=thread.id,sender=sender,text=body.strip(),nonce=nonce,admin_id=session.get('admin_id') if sender=='admin' else None)
   db.session.add(message);thread.updated_at=datetime.utcnow()
   try:
    db.session.flush()
    if attachment:db.session.add(ChatAttachment(message_id=message.id,**attachment))
    db.session.commit()
   except IntegrityError:
    db.session.rollback();message=ChatMessage.query.filter_by(thread_id=thread.id,sender=sender,nonce=nonce).first()
    if not message:raise
   return jsonify(id=message.id),201
  after=max(0,request.args.get('after',0,type=int) or 0)
  messages=ChatMessage.query.filter(ChatMessage.thread_id==thread.id,ChatMessage.id>after).order_by(ChatMessage.id).limit(100).all()
  response=jsonify(messages=[message_json(m,sender) for m in messages],thread_id=thread.id,more=len(messages)==100)
  response.headers['Cache-Control']='no-store';return response
 @app.route('/account/chat')
 def customer_chat():
  if not s.current_customer():return redirect(url_for('login'))
  return render_template('customer_chat.html')
 @app.route('/api/account/chat',methods=['GET','POST'])
 def customer_chat_messages():
  if not s.current_customer():return jsonify(error='Please sign in again.'),401
  thread=customer_thread(create=request.method=='POST')
  if not thread:return jsonify(messages=[],more=False)
  return conversation(thread,'customer')
 @app.route('/admin/chat')
 def admin_chat():return render_template('admin_chat.html',threads=ChatThread.query.order_by(ChatThread.updated_at.desc()).all(),thread=None)
 @app.route('/admin/chat/<int:thread_id>')
 def admin_chat_thread(thread_id):
  thread=db.get_or_404(ChatThread,thread_id)
  return render_template('admin_chat.html',threads=ChatThread.query.order_by(ChatThread.updated_at.desc()).all(),thread=thread)
 @app.route('/admin/chat/<int:thread_id>/messages',methods=['GET','POST'])
 def admin_chat_messages(thread_id):return conversation(db.get_or_404(ChatThread,thread_id),'admin')
 @app.route('/admin/chat/inbox')
 def admin_chat_inbox():
  term=request.args.get('q','').strip()[:100]
  query=ChatThread.query.join(s.User)
  if term:
   matching=ChatMessage.query.filter(ChatMessage.thread_id==ChatThread.id,ChatMessage.text.contains(term,autoescape=True)).exists()
   query=query.filter(db.or_(s.User.name.contains(term,autoescape=True),matching))
  threads=query.order_by(ChatThread.updated_at.desc(),ChatThread.id.desc()).limit(101).all()
  more=len(threads)>100;threads=threads[:100];ids=[t.id for t in threads]
  reader='admin:'+str(session['admin_id'])
  unread=dict(db.session.query(ChatMessage.thread_id,db.func.count(ChatMessage.id)).outerjoin(ChatRead,db.and_(ChatRead.thread_id==ChatMessage.thread_id,ChatRead.reader==reader)).filter(ChatMessage.thread_id.in_(ids),ChatMessage.sender=='customer',ChatMessage.id>db.func.coalesce(ChatRead.last_id,0)).group_by(ChatMessage.thread_id).all())
  last_ids=db.session.query(db.func.max(ChatMessage.id)).filter(ChatMessage.thread_id.in_(ids)).group_by(ChatMessage.thread_id)
  latest={m.thread_id:m for m in ChatMessage.query.filter(ChatMessage.id.in_(last_ids)).all()}
  attachments={mid:(mime,name) for mid,mime,name in db.session.query(ChatAttachment.message_id,ChatAttachment.mime,ChatAttachment.filename).filter(ChatAttachment.message_id.in_([m.id for m in latest.values()])).all()}
  results=[]
  for t in threads:
   message=latest.get(t.id);preview='No messages yet'
   if message:
    preview=message.text
    if message.id in attachments:
     mime,name=attachments[message.id];label='Voice note' if mime.startswith('audio/') else 'Photo' if mime.startswith('image/') else 'File: '+name
     preview=(preview+' · '+label) if preview else label
    preview=('Support: ' if message.sender=='admin' else '')+preview
   results.append({'id':t.id,'name':t.user.name,'avatar':customer_avatar(t),'url':url_for('admin_chat_thread',thread_id=t.id),'updated':t.updated_at.isoformat()+'Z','preview':preview[:180],'unread':unread.get(t.id,0)})
  response=jsonify(threads=results,more=more);response.headers['Cache-Control']='no-store';return response
 def attachment_response(attachment_id,admin=False):
  attachment=db.get_or_404(ChatAttachment,attachment_id);message=db.get_or_404(ChatMessage,attachment.message_id)
  if not admin:
   user=s.current_customer();thread=db.get_or_404(ChatThread,message.thread_id)
   if not user or thread.user_id!=user.id:abort(404)
  response=send_file(io.BytesIO(attachment.data),mimetype=attachment.mime,as_attachment=not attachment.mime.startswith(('image/','audio/')) or request.args.get('download')=='1',download_name=attachment.filename)
  response.headers['Cache-Control']='private, no-store';response.headers['X-Content-Type-Options']='nosniff';response.headers['Content-Security-Policy']="default-src 'none'; sandbox";return response
 @app.route('/account/chat/attachments/<int:attachment_id>')
 def customer_chat_attachment(attachment_id):return attachment_response(attachment_id)
 @app.route('/admin/chat/attachments/<int:attachment_id>')
 def admin_chat_attachment(attachment_id):return attachment_response(attachment_id,True)
 def alerts(admin=False):
  user=s.current_customer() if not admin else None
  if not admin and not user:return jsonify(error='Please sign in again.'),401
  reader=('admin:'+str(session['admin_id'])) if admin else ('customer:'+str(user.id))
  if request.method=='POST':
   data=request.get_json(silent=True) or {};thread=db.get_or_404(ChatThread,data.get('thread_id'))
   if not admin and thread.user_id!=user.id:abort(404)
   last=data.get('last_id')
   if not isinstance(last,int) or not ChatMessage.query.filter_by(id=last,thread_id=thread.id).first():abort(400)
   row=db.session.get(ChatRead,(reader,thread.id))
   if row:row.last_id=max(row.last_id,last)
   else:db.session.add(ChatRead(reader=reader,thread_id=thread.id,last_id=last))
   try:db.session.commit()
   except IntegrityError:db.session.rollback()
   return jsonify(ok=True)
  query=ChatMessage.query.join(ChatThread,ChatThread.id==ChatMessage.thread_id).outerjoin(ChatRead,db.and_(ChatRead.thread_id==ChatThread.id,ChatRead.reader==reader)).filter(ChatMessage.sender==('customer' if admin else 'admin'),ChatMessage.id>db.func.coalesce(ChatRead.last_id,0))
  if not admin:query=query.filter(ChatThread.user_id==user.id)
  count=query.count();latest=query.order_by(ChatMessage.id.desc()).first()
  response=jsonify(count=count,latest=latest.id if latest else 0,url=url_for('admin_chat_thread',thread_id=latest.thread_id) if admin and latest else url_for('admin_chat' if admin else 'customer_chat'))
  response.headers['Cache-Control']='no-store';return response
 @app.route('/api/account/chat/alerts',methods=['GET','POST'])
 def customer_chat_alerts():return alerts()
 @app.route('/admin/chat/alerts',methods=['GET','POST'])
 def admin_chat_alerts():return alerts(True)
 @app.after_request
 def private_chat(response):
  if request.endpoint in ('customer_chat','customer_chat_messages','admin_chat','admin_chat_thread','admin_chat_messages','admin_chat_inbox'):response.headers['Cache-Control']='no-store'
  return response
 return ChatThread,ChatMessage,ChatAttachment,ChatRead
