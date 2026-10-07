/* v2 policy: adversarial recipient-static and both received ephemeral roles. */
static void low_public(uint8_t*p,unsigned k,unsigned alias){
 memset(p,0,32);if(k==1)p[0]=1;if(k>=2){memset(p,255,32);p[31]=127;p[0]=(uint8_t)(236+k-2);}if(alias)p[31]|=128;
}
static void failed_state(NoiseHandshakeState*h){
 NoiseCipherState*a=0,*b=0;CHECK(noise_handshakestate_get_action(h)==NOISE_ACTION_FAILED);
 CHECK(noise_handshakestate_split(h,&a,&b)==NOISE_ERROR_INVALID_STATE);CHECK(!a&&!b);
}
static void strict_handshakes(void){
 NoiseHandshakeState*mac,*dell;NoiseBuffer w,p;uint8_t msg[128],empty[1],pub[32];
 for(unsigned k=0;k<5;k++)for(unsigned alias=0;alias<2;alias++){
  low_public(pub,k,alias);create(&mac,&dell,0);
  int rc=noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(mac),pub,32);
  if(k==0&&!alias){CHECK(rc==NOISE_ERROR_INVALID_PUBLIC_KEY);}else{
   CHECK(!rc);noise_buffer_set_output(w,msg,sizeof(msg));noise_buffer_set_input(p,empty,0);
   CHECK(noise_handshakestate_write_message(mac,&w,&p)==NOISE_ERROR_INVALID_PUBLIC_KEY);CHECK(!w.size);failed_state(mac);
  }
  destroy(mac,dell);
  create(&mac,&dell,0);noise_buffer_set_output(w,msg,sizeof(msg));noise_buffer_set_input(p,empty,0);
  CHECK(!noise_handshakestate_write_message(mac,&w,&p));memcpy(msg,pub,32);
  noise_buffer_set_output(p,empty,sizeof(empty));CHECK(noise_handshakestate_read_message(dell,&w,&p)==NOISE_ERROR_INVALID_PUBLIC_KEY);CHECK(!p.size);failed_state(dell);destroy(mac,dell);
  create(&mac,&dell,0);noise_buffer_set_output(w,msg,sizeof(msg));noise_buffer_set_input(p,empty,0);
  CHECK(!noise_handshakestate_write_message(mac,&w,&p));noise_buffer_set_output(p,empty,sizeof(empty));CHECK(!noise_handshakestate_read_message(dell,&w,&p));
  noise_buffer_set_output(w,msg,sizeof(msg));noise_buffer_set_input(p,empty,0);CHECK(!noise_handshakestate_write_message(dell,&w,&p));memcpy(msg,pub,32);
  noise_buffer_set_output(p,empty,sizeof(empty));CHECK(noise_handshakestate_read_message(mac,&w,&p)==NOISE_ERROR_INVALID_PUBLIC_KEY);CHECK(!p.size);failed_state(mac);destroy(mac,dell);
 }
}
