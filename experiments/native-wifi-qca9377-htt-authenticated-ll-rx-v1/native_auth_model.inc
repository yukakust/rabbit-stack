/* Synthetic fixture only: external core callbacks below are explicitly modeled,
 * not an actual mature handshake or production controlled-port grant. */
static QauthRawCandidate auth_candidate;
static void auth_model_send(void){
 QcaHttDataPath*d=glue_model.data;QcaHttRuntime*t=d->runtime;
 assert(!glue_station.core_completed&&!sta_local_eligibility_live(&glue_station,d->radio));
 QauthRawCandidate untouched;memset(&untouched,0xa5,sizeof untouched);auth_candidate=untouched;
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now_us,&auth_candidate));
 assert(!memcmp(&auth_candidate,&untouched,sizeof untouched));
 assert(sta_core_state(&glue_station,d->epoch,9));
 assert(sta_core_protection(&glue_station,d->epoch,glue_peer,3,1));
 assert(sta_local_eligibility_live(&glue_station,d->radio));
 uint8_t*p=t->extra[0].host;memset(p,0,2048);
 uint64_t pn=key_pn.key[0].initial+1;
 bp(p+4,0x80000040u);bp(p+12,7|(1u<<11)|(1u<<13)|(12u<<16)|(6u<<28));
 bp(p+16,(uint32_t)pn);bp(p+20,(uint32_t)(pn>>32));bp(p+24,64);bp(p+56,3u<<14);p[44]=32;
 uint8_t*f=p+300;f[0]=8;f[1]=0x42;memcpy(f+4,glue_station.own_mac,6);memcpy(f+10,glue_peer,6);memcpy(f+16,glue_peer,6);f[22]=12<<4;
 uint8_t*iv=f+24;iv[0]=pn;iv[1]=pn>>8;iv[3]=32;for(unsigned j=0;j<4;j++)iv[4+j]=pn>>(16+8*j);
 uint8_t*l=f+32;l[0]=0xaa;l[1]=0xaa;l[2]=3;l[6]=8;for(unsigned j=8;j<20;j++)l[j]=(uint8_t)(0x90+j);
 uint8_t ind[16]={18,16,7,0,0,0,1,0};bp(ind+8,t->owners[0].paddr);ind[12]=64;
 emit_htt(ind,16);auth_sent=1;
}
int auth_model_copy(uint64_t now){
 if(data_case!=30||!auth_sent)return 0;
 QcaHttDataPath*d=glue_model.data;if(!d->pending_valid)return 0;
 QpnLedger original=key_pn;QauthRawCandidate untouched;memset(&untouched,0xa5,sizeof untouched);
 auth_candidate=untouched;
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now+1,&auth_candidate));
 assert(sta_core_state(&glue_station,d->epoch,8));
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(sta_core_state(&glue_station,d->epoch,9));
 assert(sta_core_protection(&glue_station,d->epoch,glue_peer,0,1));
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(sta_core_protection(&glue_station,d->epoch,glue_peer,3,1));
 QsgKeyOp bad=key_operations[0];bad.phase=QSK_FAULT;auth_candidate=untouched;
 assert(!qauth_native_candidate(&glue_model,&bad,&key_operations[1],&key_pn,now,&auth_candidate));
 assert(!memcmp(&auth_candidate,&untouched,sizeof untouched)&&!memcmp(&key_pn,&original,sizeof original));
 bad=key_operations[0];bad.epoch++;assert(!qauth_native_candidate(&glue_model,&bad,&key_operations[1],&key_pn,now,&auth_candidate));
 bad=key_operations[0];bad.pub_cookie=0;assert(!qauth_native_candidate(&glue_model,&bad,&key_operations[1],&key_pn,now,&auth_candidate));
 bad=key_operations[0];bad.dma_serial=0;assert(!qauth_native_candidate(&glue_model,&bad,&key_operations[1],&key_pn,now,&auth_candidate));
 QcaBootNative*b=d->radio->startup->operating->boot;
 b->asset->received^=1;assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));b->asset->received^=1;
 size_t capacity=b->asset->capacity;b->asset->capacity=b->asset->policy.total-1;assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));b->asset->capacity=capacity;
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,(QauthRawCandidate*)d->runtime->extra[1].host));
 b->asset->policy.digest[0]^=1;assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));b->asset->policy.digest[0]^=1;
 uint8_t*p=d->runtime->extra[0].host;uint32_t att=bw(p+4);bp(p+4,att|(1u<<29));assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));bp(p+4,att);
 assert(qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(!memcmp(&key_pn,&original,sizeof original));
 assert(auth_candidate.provenance.pn==key_pn.key[0].initial+1&&auth_candidate.ethernet_bytes==26&&auth_candidate.frame_bytes==44&&!(auth_candidate.frame[1]&64));
 assert(auth_candidate.ethernet[14]==0x98&&d->runtime->owners[0].state==2&&d->runtime->rx_copy_owners==1&&d->runtime->port->dma_users==47);
 QpnLedger staged=auth_candidate.staged;auth_candidate=untouched;
 assert(!qauth_native_candidate(&glue_model,&key_operations[0],&key_operations[1],&staged,now,&auth_candidate)); /* key-op ledger identity mismatch */
 assert(!qauth_native_commit(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(!memcmp(&key_pn,&original,sizeof original));
 memset(&auth_candidate,0,sizeof auth_candidate);
 assert(qauth_native_commit(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(key_pn.key[0].last[16]==original.key[0].initial+1&&key_pn.last_completion==d->pending.completion);
 QpnLedger committed=key_pn;
 assert(!qauth_native_commit(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate));
 assert(!memcmp(&committed,&key_pn,sizeof committed));
 memset(&auth_candidate,0,sizeof auth_candidate);
 assert(!qauth_native_commit(&glue_model,&key_operations[0],&key_operations[1],&key_pn,now,&auth_candidate)); /* same owned addr replay */
 assert(!memcmp(&committed,&key_pn,sizeof committed));
 assert(d->runtime->owners[0].state==2&&d->runtime->rx_copy_owners==1&&d->runtime->port->dma_users==47);
 puts("ACTUAL PRODUCER OWNED47+REAL KEY DMA/SEC+OFFICIAL ASSET+RAW HW FLAGS+ATOMIC OUTPUT PN COMMIT+REPLAY PASS; CORE CALLBACK STATE SYNTHETIC; NO PORT/IP");exit(0);
}
