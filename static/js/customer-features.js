(() => {
 const couponInput=document.getElementById('coupon-code');
 const checkoutSummary=document.getElementById('checkoutSummary');
 const originalSubtotal=checkoutSummary?.dataset.subtotal;
 couponInput?.addEventListener('input',()=>{if(checkoutSummary){checkoutSummary.dataset.subtotal=originalSubtotal;document.getElementById('delivery_area_id').dispatchEvent(new Event('change'));document.getElementById('coupon-feedback').textContent='Apply the code to preview your discount.';}});
 const csrf=document.querySelector('meta[name="csrf-token"]')?.content;
 const search=document.getElementById('store-search');let timer,sequence=0;
 search?.addEventListener('input',()=>{clearTimeout(timer);const current=++sequence;timer=setTimeout(async()=>{try{
 const response=await fetch('/api/products/suggestions?q='+encodeURIComponent(search.value));if(!response.ok)return;
 const entries=await response.json();if(current!==sequence)return;
 const list=document.getElementById('search-suggestions');list.replaceChildren(...entries.map(item=>{const option=document.createElement('option');option.value=item.name;return option;}));
 }catch(e){}},200);});
 const tracker=document.getElementById('order-tracker');
 if(tracker){setInterval(async()=>{if(document.hidden)return;try{
 const response=await fetch(tracker.dataset.url,{cache:'no-store'});if(!response.ok)throw Error();const data=await response.json();
 document.getElementById('tracking-status').textContent=data.tracking;document.getElementById('delivery-estimate').textContent=data.estimate;document.getElementById('payment-status').textContent=data.payment;
 tracker.querySelectorAll('[data-status]').forEach(item=>item.classList.toggle('current',item.dataset.status===data.status));
 document.getElementById('tracking-feedback').textContent='Updated just now. Checking every 15 seconds.';
 }catch(e){document.getElementById('tracking-feedback').textContent='Unable to refresh. Your last known status is shown.';}},15000);}
 document.getElementById('saved-address')?.addEventListener('change',event=>{const option=event.target.selectedOptions[0];if(!option.dataset.name)return;for(const [key,value] of Object.entries({customer_name:option.dataset.name,phone:option.dataset.phone,location:option.dataset.location})){document.querySelector('[name="'+key+'"]').value=value;}});
 document.getElementById('apply-coupon')?.addEventListener('click',async()=>{
 const feedback=document.getElementById('coupon-feedback');try{const response=await fetch('/api/cart/coupon',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},body:JSON.stringify({code:document.getElementById('coupon-code').value})});const data=await response.json();if(!response.ok)throw Error(data.error);
 feedback.textContent='Discount: UGX '+data.discount.toLocaleString()+' (delivery excluded).';
 const summary=document.getElementById('checkoutSummary');summary.dataset.subtotal=String(data.subtotal-data.discount);document.getElementById('delivery_area_id').dispatchEvent(new Event('change'));
 }catch(e){feedback.textContent=e.message||'Unable to check coupon.';}});
 const pushFeedback=document.getElementById('push-feedback');
 document.getElementById('enable-push')?.addEventListener('click',async()=>{try{
 if(!('serviceWorker' in navigator)||!('PushManager' in window))throw Error('Notifications are not supported in this browser.');
 const config=await (await fetch('/api/push/config')).json();if(!config.publicKey)throw Error('Notifications are not available yet.');
 if(await Notification.requestPermission()!=='granted')throw Error('Notifications were not enabled.');
 const registration=await navigator.serviceWorker.register('/service-worker.js');await navigator.serviceWorker.ready;
 const key=Uint8Array.from(atob(config.publicKey.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
 const subscription=await registration.pushManager.getSubscription()||await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key});
 const response=await fetch('/api/push/subscription',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},body:JSON.stringify({subscription,promotions:document.getElementById('promo-opt-in').checked})});if(!response.ok)throw Error('Unable to save notification preferences.');pushFeedback.textContent='Notifications enabled for this browser.';
 }catch(e){pushFeedback.textContent=e.message;}});
 document.getElementById('disable-push')?.addEventListener('click',async()=>{try{
 const registration=await navigator.serviceWorker.getRegistration();const subscription=await registration?.pushManager.getSubscription();
 if(subscription){const response=await fetch('/api/push/subscription',{method:'DELETE',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},body:JSON.stringify({subscription})});if(!response.ok)throw Error('Unable to update preferences.');await subscription.unsubscribe();}
 pushFeedback.textContent='Notifications turned off.';
 }catch(e){pushFeedback.textContent=e.message;}});
})();
