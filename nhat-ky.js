// Ghi lịch sử thao tác (tên người dùng + cookie) lên Supabase.
// Cấu hình kết nối nằm trong config.js (URL và publishable key, được phép công khai).
(function(){
  const C=window.TRA_CUU_CONFIG||{};
  const ON=!!(C.supabaseUrl&&C.supabaseKey);
  const DAYS=365;
  const getC=k=>{const m=document.cookie.match(new RegExp('(?:^|; )'+k+'=([^;]*)'));return m?decodeURIComponent(m[1]):''};
  const setC=(k,v)=>{document.cookie=k+'='+encodeURIComponent(v)+';max-age='+(DAYS*86400)+';path=/;SameSite=Lax'+(location.protocol==='https:'?';Secure':'')};
  const uuid=()=>(crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2));
  let q=[],timer=null;
  function flush(keep){
    if(!ON||!q.length)return;
    const body=JSON.stringify(q.splice(0));
    fetch(C.supabaseUrl+'/rest/v1/tracuu_nhat_ky',{method:'POST',keepalive:!!keep,headers:{'apikey':C.supabaseKey,'Authorization':'Bearer '+C.supabaseKey,'Content-Type':'application/json','Prefer':'return=minimal'},body}).catch(()=>{});
  }
  function log(action,detail){
    const ten=getC('tc_ten'),dev=getC('tc_may');
    if(!ten)return;
    q.push({ten_nguoi_dung:ten.slice(0,80),ma_thiet_bi:dev.slice(0,64),thao_tac:action,chi_tiet:detail||{},trinh_duyet:navigator.userAgent.slice(0,300)});
    clearTimeout(timer);timer=setTimeout(flush,2500);
  }
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')flush(true)});
  window.addEventListener('pagehide',()=>flush(true));
  // Bắt buộc đồng ý cookie và đặt tên trước khi dùng
  function require(done){
    if(getC('tc_ten')&&getC('tc_may')){done();return}
    const w=document.createElement('div');w.id='ten-gate';
    w.innerHTML=`<form><h2>Đặt tên người dùng</h2><p class="note" style="text-align:left">Trang này lưu cookie trên trình duyệt và ghi lại lịch sử tra cứu (tên bạn đặt, thời gian, mã đã tìm và xem) để quản lý theo dõi. Cần đồng ý và đặt tên để tiếp tục.</p><input id="ten-in" maxlength="80" placeholder="Họ tên hoặc tên đơn vị"><label class="ck" style="justify-content:flex-start;text-align:left"><input type="checkbox" id="ten-ok"> Tôi đồng ý lưu cookie và ghi lịch sử thao tác</label><button type="submit">Tiếp tục</button><div id="ten-err" style="color:#c00;font-size:13px;min-height:18px"></div></form>`;
    document.body.appendChild(w);
    const inp=w.querySelector('#ten-in');inp.value=getC('tc_ten');inp.focus();
    w.querySelector('form').onsubmit=e=>{
      e.preventDefault();const t=inp.value.trim();
      if(t.length<2){w.querySelector('#ten-err').textContent='Vui lòng nhập tên (ít nhất 2 ký tự)';return}
      if(!w.querySelector('#ten-ok').checked){w.querySelector('#ten-err').textContent='Cần đồng ý lưu cookie để sử dụng';return}
      setC('tc_ten',t);if(!getC('tc_may'))setC('tc_may',uuid());
      if(getC('tc_ten')!==t){w.querySelector('#ten-err').textContent='Trình duyệt đang chặn cookie. Hãy bật cookie cho trang này rồi thử lại.';return}
      w.remove();done();
    };
  }
  window.NhatKy={log,require,ten:()=>getC('tc_ten'),doiTen:()=>{setC('tc_ten','');location.reload()},bat:ON};
})();
