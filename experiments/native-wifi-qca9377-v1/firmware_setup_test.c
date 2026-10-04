/* Fresh native cache gate. No freed DMA response dereference or device I/O. */
#include "firmware_port.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned allocations,frees;
static Status EFIAPI allocate(uint32_t kind,uint64_t n,void**out){assert(kind==4&&n<=QCA_FW_MAX);*out=malloc((size_t)n);assert(*out);allocations++;return 0;}
static Status EFIAPI release(void*p){assert(p);free(p);frees++;return 0;}
#define BAD(field,value) do { __typeof__(field) saved=(field);(field)=(value);QcaFirmwarePort rejected={0};assert(qca_fwp_start_setup(&rejected,&st,&policy,&setup)<0&&!rejected.phase&&!allocations);(field)=saved;cases++; } while(0)
int main(void){
 uint64_t boot[10]={0};TableHeader*header=(TableHeader*)boot;header->signature=0x56524553544f4f42ull;header->size=80;boot[8]=(uintptr_t)allocate;boot[9]=(uintptr_t)release;
 SystemTable st={0};st.header.signature=0x5453595320494249ull;st.header.size=sizeof(st);st.boot=boot;
 QcaFirmwarePolicy policy={0};policy.owner[0]=policy.target[0]=policy.digest[0]=1;policy.total=751436;policy.type=8;policy.version=0x05020001;policy.kind=1;policy.generation=34;
 QcaUefiPort port={0};port.system=&st;QcaBootIrq irq={0};irq.port=&port;
 QcaInitAdapter adapter={0};adapter.phase=QCA_INIT_CLOSED;adapter.warm.phase=QCA_WARM_DONE;adapter.channels.phase=QCA_CHANNEL_CLOSED;adapter.channels.allocated=adapter.channels.cleanup_slot=14;adapter.mapped.irq=&irq;adapter.bus.phase=QCA_BUS_OFF;adapter.channels.bus=&adapter.bus;adapter.bus.access=&adapter.access;adapter.mapped.channels=&adapter.channels;adapter.access.port=&port;
 QcaConfigSetup setup={0};setup.phase=4;setup.op=10;setup.write_mask=setup.readback_mask=31;setup.write_attempts=5;setup.cpu_attempted=1;setup.bmi_polls=1;
 setup.read.phase=4;setup.read.mask=7;setup.read.slot=3;setup.read.full.adapter=&adapter;setup.read.full.exchange.phase=QCA_DIAG_DONE;setup.read.full.exchange.value=0x401ee0;
 setup.bmi.phase=QCA_BMI_DONE;setup.bmi.bytes=setup.bmi.info_length=12;setup.bmi.tx_done=setup.bmi.rx_done=1;setup.bmi.observed_mask=3;setup.bmi.type=8;setup.bmi.version=0x05020001;setup.bmi.tx=&adapter.channels.rings[0];setup.bmi.rx=&adapter.channels.rings[1];setup.bmi.bus=&adapter.bus;setup.bmi.request=&adapter.channels.buffers[1];setup.bmi.response=&adapter.channels.buffers[3];
 unsigned cases=0;
 BAD(setup.phase,3);BAD(setup.error,1);BAD(setup.op,9);BAD(setup.write_mask,15);BAD(setup.readback_mask,15);BAD(setup.write_attempts,4);BAD(setup.cpu_attempted,0);
 BAD(setup.bmi.phase,QCA_BMI_FAULT);BAD(setup.bmi.error,1);BAD(setup.bmi.bytes,8);BAD(setup.bmi.info_length,8);BAD(setup.bmi.tx_done,0);BAD(setup.bmi.rx_done,0);BAD(setup.bmi.observed_mask,1);BAD(setup.bmi_polls,0);BAD(setup.bmi.type,7);BAD(setup.bmi.version,0x05020002);
 BAD(setup.read.phase,3);BAD(setup.read.error,1);BAD(setup.read.mask,3);BAD(setup.read.slot,2);BAD(setup.read.full.error,1);BAD(setup.read.full.exchange.phase,QCA_DIAG_FAULT);BAD(setup.read.full.exchange.value,0x401ee4);BAD(setup.read.full.adapter,0);
 BAD(adapter.cancelled,1);BAD(adapter.warm.ce_owned,1);BAD(adapter.channels.error,1);BAD(adapter.bus.error,1);BAD(adapter.mapped.error,1);BAD(adapter.bus.phase,QCA_BUS_ACTIVE);BAD(adapter.channels.bus,0);BAD(adapter.bus.access,0);BAD(adapter.mapped.channels,0);BAD(port.system,0);BAD(adapter.access.port,0);BAD(setup.bmi.tx,0);BAD(setup.bmi.rx,0);
 BAD(adapter.phase,QCA_INIT_READY);BAD(adapter.error,1);BAD(adapter.warm.phase,QCA_WARM_IDLE);BAD(adapter.warm.error,1);BAD(adapter.warm.owned,1);BAD(adapter.recovery.owned,1);
 BAD(adapter.channels.phase,QCA_CHANNEL_IDLE);BAD(adapter.channels.allocated,13);BAD(adapter.channels.cleanup_slot,13);BAD(adapter.access.count,1);BAD(adapter.bus.owned,1);
 BAD(adapter.mapped.irq,0);BAD(irq.port,0);BAD(irq.error,1);BAD(port.error,1);BAD(irq.owned,1);BAD(port.claimed,1);BAD(port.dma_users,1);BAD(port.wake_owned,1);BAD(port.link_owned,1);BAD(port.boot_irq_owned,1);
 BAD(setup.bmi.bus,0);BAD(setup.bmi.request,&adapter.channels.buffers[0]);BAD(setup.bmi.response,&adapter.channels.buffers[2]);
 for(unsigned i=0;i<14;i++){BAD(adapter.channels.buffers[i].host,(void*)1);BAD(adapter.channels.buffers[i].allocated,1);BAD(adapter.channels.buffers[i].mapped,1);BAD(adapter.channels.buffers[i].valid,1);BAD(adapter.channels.buffers[i].exposed,1);}
 BAD(policy.total,0);BAD(policy.total,QCA_FW_MAX+1);BAD(policy.kind,3);BAD(policy.generation,0);BAD(policy.owner[0],0);BAD(policy.target[0],0);BAD(policy.digest[0],0);BAD(st.header.signature,0);BAD(st.boot,0);BAD(boot[8],0);BAD(boot[9],0);
 QcaFirmwarePort receiver={0};assert(!qca_fwp_start_setup(&receiver,&st,&policy,&setup));assert(qca_fwp_start_setup(&receiver,&st,&policy,&setup)<0&&!allocations);
 /* Cached proof remains valid after all14 DMA buffers were freed. */
 assert(qca_fwp_step(&receiver)==1&&allocations==1);assert(qca_fwp_step(&receiver)==1&&allocations==2);assert(!qca_fwp_step(&receiver)&&receiver.phase==4);assert(qca_fwp_owned(&receiver));assert(qca_fwp_close(&receiver)==1&&frees==1);assert(!qca_fwp_close(&receiver)&&frees==2&&!qca_fwp_owned(&receiver));
 printf("FRESH SETUP RAM GATE PASS rejected=%u allocations=%u frees=%u\n",cases,allocations,frees);return 0;
}
