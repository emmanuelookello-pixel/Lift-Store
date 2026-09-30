/* No caching of authenticated pages or account data. */
self.addEventListener('push',event=>{
 let data={};try{data=event.data.json();}catch(e){return;}
 event.waitUntil(self.registration.showNotification(data.title||'Lift Store',{body:data.body||'',data:{url:data.url||'/'}}));
});
self.addEventListener('notificationclick',event=>{
 event.notification.close();const target=new URL(event.notification.data.url,self.location.origin);
 if(target.origin===self.location.origin)event.waitUntil(clients.openWindow(target.href));
});
