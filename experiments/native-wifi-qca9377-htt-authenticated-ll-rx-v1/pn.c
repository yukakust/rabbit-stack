#include "pn.h"
static uint32_t w(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static unsigned h(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static int same(const uint8_t*a,const uint8_t*b,unsigned n){for(unsigned j=0;j<n;j++)if(a[j]!=b[j])return 0;return 1;}
static int mac(const uint8_t*p){unsigned n=0;for(unsigned j=0;j<6;j++)n|=p[j];return n&&!(p[0]&1);}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
int qpn_begin(QpnLedger*s,uint64_t epoch,uint16_t peer,uint8_t vdev,const uint8_t ap[6],const uint8_t own[6],const QcaHttBinding*b,const QcaHttVersion*v){if(!s||s->epoch||!epoch||peer>=2048||vdev>=4||!ap||!own||!mac(ap)||!mac(own)||same(ap,own,6)||!b||!v||!b->endpoint||b->endpoint>=9||b->op_version!=3||v->major!=3||v->minor!=56||overlap(s,sizeof(*s),ap,6)||overlap(s,sizeof(*s),own,6)||overlap(s,sizeof(*s),b,sizeof(*b))||overlap(s,sizeof(*s),v,sizeof(*v)))return 0;QpnLedger n={0};n.epoch=epoch;n.peer_id=peer;n.vdev=vdev;n.htt=*b;n.version=*v;for(unsigned j=0;j<6;j++){n.peer[j]=ap[j];n.own[j]=own[j];}*s=n;return 1;}
int qpn_key_posted(QpnLedger*s,uint64_t epoch,unsigned index,const uint8_t*rsc,unsigned bytes,uint32_t floor,uint32_t ticket){if(!s||s->epoch!=epoch||s->quarantined||s->pending||index>3||s->key[index].attempted||!ticket||floor<s->last_completion||(bytes!=0&&bytes!=6)||(bytes&&(!rsc||overlap(s,sizeof(*s),rsc,bytes))))return 0;if(index&&bytes!=6)return 0;uint64_t initial=0;for(unsigned j=0;j<bytes;j++)initial|=(uint64_t)rsc[j]<<(8*j);s->pending=1;s->index=(uint8_t)index;s->pending_floor=floor;s->ticket=ticket;s->key[index].attempted=1;s->key[index].initial=initial;return 1;}
int qpn_key_sec(QpnLedger*s,uint64_t epoch,const QcaRxEvent*e){if(!s||!e||s->epoch!=epoch||s->quarantined||!s->pending||e->completion<=s->pending_floor||overlap(s,sizeof(*s),e,sizeof(*e)))return 0;StaEvent event={0};if(sta_decode_htt_bound(e,&s->htt,&s->version,&event)!=1||event.kind!=STA_SEC_IND)return 0;if(event.peer_id!=s->peer_id||event.cipher!=6||event.unicast!=(s->index==0)){s->quarantined=1;s->pending=0;return 0;}QpnKey*k=&s->key[s->index];k->confirmed=1;k->sec_completion=e->completion;for(unsigned j=0;j<17;j++)k->last[j]=k->initial;s->last_completion=e->completion;s->pending=0;return 1;}
int qpn_counter_owned(QpnLedger*s,const QRxInd*ind,const QRxOwner*owner,const uint8_t*p,unsigned bytes,QpnView*out){
 if(!s||!ind||!owner||!p||!out||s->quarantined||s->pending||bytes!=2048||owner->bytes!=2048||owner->state!=2||!owner->map_identity||owner->epoch!=s->epoch||ind->epoch!=s->epoch||owner->completion!=ind->completion||ind->completion<s->last_completion||!owner->paddr||(owner->paddr&7)||owner->paddr>UINT32_MAX-2047||overlap(out,sizeof(*out),s,sizeof(*s))||overlap(out,sizeof(*out),ind,sizeof(*ind))||overlap(out,sizeof(*out),owner,sizeof(*owner))||overlap(out,sizeof(*out),p,bytes)||overlap(s,sizeof(*s),p,bytes)||overlap(s,sizeof(*s),ind,sizeof(*ind))||overlap(s,sizeof(*s),owner,sizeof(*owner)))return QPN_REJECTED;
 QRxInd parsed={0};if(qrx_indication(3,3,56,ind->epoch,ind->completion,s->last_completion-(ind->completion==s->last_completion&&s->last_completion!=0),ind->raw,ind->raw_bytes,&parsed)!=1||parsed.kind!=18||!parsed.usable||parsed.offload||parsed.frag||parsed.peer!=s->peer_id||parsed.vdev!=s->vdev||parsed.tid>16)return QPN_UNSUPPORTED;
 if(parsed.peer!=ind->peer||parsed.vdev!=ind->vdev||parsed.tid!=ind->tid||parsed.count!=ind->count)return QPN_REJECTED;
 if(ind->completion==s->last_completion)for(unsigned j=0;j<s->seen_count;j++)if(s->seen[j]==owner->paddr)return QPN_REJECTED;
 unsigned at=parsed.count;for(unsigned j=0;j<parsed.count;j++)if(parsed.paddr[j]==owner->paddr){at=j;break;}if(at==parsed.count||parsed.fw_desc[at])return QPN_REJECTED;
 QRxFrame frame={0};if(!qrx_frame(p,bytes,parsed.length[at],&frame))return QPN_REJECTED;
 uint32_t info=w(p+12),info1=w(p+20);unsigned cipher=info>>28,peer=info&2047;
 if(!frame.encrypted||cipher!=6||peer!=s->peer_id||(frame.attention&((1u<<24)|(1u<<3)|(1u<<4))))return QPN_UNSUPPORTED;
 const uint8_t*f=p+300;unsigned fc=h(f),qos=(fc&0x80)!=0,hdr=qos?26:24;
 if((fc&0xfc)!=(qos?0x88:0x08)||(fc&0x0300)!=0x0200||!(fc&0x4000)||(fc&0x8400)||frame.bytes<hdr+8||!same(f+10,s->peer,6)||(h(f+22)&15))return QPN_UNSUPPORTED;
 unsigned tid=qos?(f[24]&15):16;if(qos&&(f[24]&0x80))return QPN_UNSUPPORTED;
 if(tid!=parsed.tid||(qos&&tid!=(info1>>28))||frame.seq!=(h(f+22)>>4))return QPN_REJECTED;
 const uint8_t*iv=f+hdr;if(iv[2]||(iv[3]&63)!=32||p[44]!=iv[3])return QPN_REJECTED;
 unsigned index=iv[3]>>6,multicast=f[4]&1;if(multicast!=((frame.attention>>2)&1)||(!qos)!=((frame.attention>>6)&1))return QPN_REJECTED;if((index==0&&multicast)||(index!=0&&!multicast)||(!multicast&&!same(f+4,s->own,6)))return QPN_REJECTED;
 QpnKey*k=&s->key[index];if(!k->confirmed||ind->completion<=k->sec_completion)return QPN_REJECTED;
 uint64_t pn=(uint64_t)w(p+16)|((uint64_t)(info1&65535)<<32),header_pn=iv[0]|((uint64_t)iv[1]<<8)|((uint64_t)iv[4]<<16)|((uint64_t)iv[5]<<24)|((uint64_t)iv[6]<<32)|((uint64_t)iv[7]<<40);
 if(pn!=header_pn||pn<=k->last[tid])return QPN_REJECTED;
 QpnView v={pn,s->epoch,ind->completion,owner->map_identity,owner->paddr,s->peer_id,(uint16_t)frame.seq,(uint8_t)index,(uint8_t)tid,(uint8_t)multicast,frame.attention};if(ind->completion>s->last_completion)s->seen_count=0;if(s->seen_count==QRX_MAX)return QPN_REJECTED;s->seen[s->seen_count++]=owner->paddr;k->last[tid]=pn;s->last_completion=ind->completion;*out=v;return QPN_COUNTER_ACCEPTED;
}
void qpn_revoke(QpnLedger*s,uint64_t epoch){if(s&&s->epoch==epoch)s->quarantined=1;}
