/* ROM indicator profile from pinned ath10k qca6174_regs/hw.h/pci.c. */
#include "rom_ready.h"
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static int valid(QcaUefiPort*p){return p&&p->claimed&&p->validated&&p->pci&&p->memory_ready&&p->wake_owned&&p->bar_extent>=0x3a02c;}
static int fail(QcaRomReady*r,unsigned error){r->phase=QCA_ROM_FAULT;r->error=error;return -1;}
int qca_rom_begin(QcaRomReady*r,QcaUefiPort*p,uint64_t now){
 if(!r||!valid(p)||now>UINT64_MAX-3000000)return -1;
 r->port=p;r->started=r->last=r->next=now;r->indicator=r->reads=r->error=0;r->phase=QCA_ROM_WAIT;return 0;
}
int qca_rom_poll(QcaRomReady*r,uint64_t now){
 if(!r)return -1;
 if(r->phase==QCA_ROM_READY)return valid(r->port)?1:fail(r,1);
 if(r->phase!=QCA_ROM_WAIT)return -1;
 if(!valid(r->port))return fail(r,1);
 if(now<r->last)return fail(r,2);
 r->last=now;
 if(now-r->started>=3000000)return fail(r,r->indicator==UINT32_MAX?3:4);
 if(now<r->next)return 0;
 r->next=now>UINT64_MAX-10000?UINT64_MAX:now+10000;
 void*fn=*(void**)((uint8_t*)r->port->pci+16);
 if(((Memory)fn)(r->port->pci,2,0,0x3a028,1,&r->indicator))return fail(r,5);
 r->reads++;
 /* All ones may be transient during boot; never treat it as initialized. */
 if(r->indicator==UINT32_MAX)return 0;
 if(r->indicator&1)return fail(r,6);
 if(r->indicator&2){r->phase=QCA_ROM_READY;return 1;}
 return 0;
}
