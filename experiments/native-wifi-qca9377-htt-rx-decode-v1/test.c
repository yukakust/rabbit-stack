#include "rx_decode.h"
#include "runs/oracle_types.h"
#include <assert.h>
#include <string.h>
static unsigned checks;
static void put(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8));}
static void half(uint8_t*p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static unsigned inord(uint8_t*p,unsigned count){memset(p,0,2048);p[0]=0x12;half(p+6,count);for(unsigned i=0;i<count;i++){put(p+8+i*8,0x10000+i*2048);half(p+12+i*8,24);}return 8+8*count;}
static QRxRing ring(QRxOwner*entries,unsigned count){for(unsigned i=0;i<count;i++)entries[i]=(QRxOwner){0x10000+i*2048,2048,1,1,0,9+i/32};return (QRxRing){3,3,56,1,1,10,10,count,entries};}
int main(void){
 assert(sizeof(struct htt_rx_desc_v1)==300&&offsetof(struct htt_rx_desc_v1,attention)==4&&offsetof(struct htt_rx_desc_v1,frag_info.common.ring2_more_count)==10&&offsetof(struct htt_rx_desc_v1,msdu_start.common.info0)==24&&offsetof(struct htt_rx_desc_v1,msdu_start.common.info1)==32&&offsetof(struct htt_rx_desc_v1,msdu_end.common.info0)==56&&offsetof(struct htt_rx_desc_v1,msdu_payload)==300);checks++;
 assert(sizeof(struct htt_rx_indication_hdr)==7&&sizeof(struct htt_rx_indication_ppdu)==36&&sizeof(struct htt_rx_indication_prefix)==4&&sizeof(struct htt_rx_in_ord_ind)==7&&sizeof(struct htt_rx_in_ord_msdu_desc)==8);checks++;
 QRxInd i,sentinel;memset(&sentinel,0xa5,sizeof(sentinel));uint8_t raw[2048],copy[2048];unsigned n=inord(raw,2);i=sentinel;assert(qrx_indication(3,3,56,1,11,10,raw,n,&i)==1&&i.usable&&i.count==2&&i.paddr[1]==0x10800);checks++;
 for(unsigned len=0;len<n;len++){QRxInd out=sentinel;assert(!qrx_indication(3,3,56,1,11,10,raw,len,&out)&&!memcmp(&out,&sentinel,sizeof(out)));checks++;}
 for(unsigned x=0;x<256;x++)if(x!=1&&x!=0x12){raw[0]=(uint8_t)x;assert(qrx_indication(3,3,56,1,11,10,raw,n,&i)==2&&!i.usable&&!memcmp(i.raw,raw,n));checks++;}raw[0]=0x12;
 for(unsigned flag=5;flag<8;flag++){raw[1]=(uint8_t)(1u<<flag);assert(qrx_indication(3,3,56,1,11,10,raw,n,&i)==1&&!i.usable);checks++;}raw[1]=0;
 assert(!qrx_indication(3,3,55,1,11,10,raw,n,&i)&&!qrx_indication(2,3,56,1,11,10,raw,n,&i)&&!qrx_indication(3,3,56,1,10,10,raw,n,&i));checks+=3;
 assert(qrx_indication(3,3,56,1,11,10,raw,n,&i)==1);QRxOwner entries[2048],before[3];QRxRing r=ring(entries,3);memcpy(before,entries,sizeof(before));QRxInd bad=i;bad.paddr[1]=0xdead000;assert(!qrx_claim(&r,&bad)&&!memcmp(before,entries,sizeof(before))&&r.last==10);checks++;
 bad=i;bad.paddr[1]=bad.paddr[0];assert(!qrx_claim(&r,&bad)&&!memcmp(before,entries,sizeof(before)));checks++;
 for(unsigned mode=0;mode<7;mode++){r=ring(entries,3);memcpy(before,entries,sizeof(before));if(mode==0)r.full_reorder=0;if(mode==1)entries[1].paddr=entries[0].paddr+8;if(mode==2)entries[1].state=2;if(mode==3)entries[1].epoch=2;if(mode==4)entries[1].map_identity=0;if(mode==5)entries[1].bytes=4096;if(mode==6)entries[1].paddr=0xfffffff8;memcpy(before,entries,sizeof(before));assert(!qrx_claim(&r,&i)&&!memcmp(before,entries,sizeof(before)));checks++;}
 r=ring(entries,1023);assert(qrx_claim(&r,&i)&&r.last==11&&entries[0].state==2&&entries[1].state==2&&entries[1022].state==1);checks++;
 assert(!qrx_claim(&r,&i)&&!qrx_retire(&r,entries[0].paddr,2,11)&&!qrx_retire(&r,entries[0].paddr,1,12)&&qrx_retire(&r,entries[0].paddr,1,11)&&!qrx_retire(&r,entries[0].paddr,1,11));checks+=5;
 n=inord(raw,255);assert(qrx_indication(3,3,56,1,12,10,raw,n,&i)==1&&i.count==255);r=ring(entries,1023);assert(qrx_claim(&r,&i));checks+=2;
 /* RX_IND uses exact primary struct sizes, one nonoverlapping MPDU range. */
 memset(raw,0,sizeof(raw));raw[0]=1;raw[7]=1;half(raw+44,3);unsigned at=1+sizeof(struct htt_rx_indication_hdr)+sizeof(struct htt_rx_indication_ppdu)+sizeof(struct htt_rx_indication_prefix)+4;raw[at]=2;raw[at+1]=1;n=at+sizeof(struct htt_rx_indication_mpdu_range);assert(qrx_indication(3,3,56,1,13,10,raw,n,&i)==1&&i.ranges==1&&i.fw_bytes==3&&i.mpdu_count==2&&i.usable);assert(!qrx_claim(&r,&i));checks+=2;
 for(unsigned len=0;len<n;len++){QRxInd out=sentinel;assert(!qrx_indication(3,3,56,1,13,10,raw,len,&out));checks++;}
 raw[at+1]=8;assert(qrx_indication(3,3,56,1,13,10,raw,n,&i)==1&&!i.usable&&i.range_status[0]==8);checks++;
 raw[at+1]=1;raw[1]=0x60;assert(qrx_indication(3,3,56,1,13,10,raw,n,&i)==1&&!i.usable&&i.flush&&i.release);checks++;
 QRxFrame f,old;memset(&old,0xa5,sizeof(old));memset(raw,0,sizeof(raw));put(raw+offsetof(struct htt_rx_desc_v1,attention),RX_ATTENTION_FLAGS_MSDU_DONE);put(raw+offsetof(struct htt_rx_desc_v1,msdu_start.common.info0),24);put(raw+offsetof(struct htt_rx_desc_v1,msdu_end.common.info0),RX_MSDU_END_INFO0_FIRST_MSDU|RX_MSDU_END_INFO0_LAST_MSDU);assert(qrx_frame(raw,324,24,&f)&&f.bytes==24);checks++;
 for(unsigned len=0;len<324;len++){f=old;assert(!qrx_frame(raw,len,24,&f)&&!memcmp(&f,&old,sizeof(f)));checks++;}
 memcpy(copy,raw,sizeof(raw));for(unsigned flag=0;flag<32;flag++){if(flag!=13&&flag!=16&&flag!=17&&flag!=26&&flag!=27&&flag!=28&&flag!=29&&flag!=30)continue;put(raw+4,RX_ATTENTION_FLAGS_MSDU_DONE|(1u<<flag));assert(!qrx_frame(raw,324,24,&f));checks++;}memcpy(raw,copy,sizeof(raw));
 for(unsigned mode=0;mode<8;mode++){memcpy(raw,copy,sizeof(raw));if(mode==0)put(raw+4,0);if(mode==1)raw[10]=1;if(mode==2)put(raw+32,0x100);if(mode==3)put(raw+56,RX_MSDU_END_INFO0_LAST_MSDU);if(mode==4)put(raw+24,1749);if(mode==5)raw[301]=4;if(mode==6)raw[322]=1;if(mode==7)put(raw+24,25);assert(!qrx_frame(raw,324,24,&f));checks++;}
 printf("PASS %u pure HTT3.56 RX ABI/ownership/frame cases; SYNTHETIC NOT PHYSICAL\n",checks);return 0;
}
