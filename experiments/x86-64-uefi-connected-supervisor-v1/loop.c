/* Included after the generated resident supervisor: no second HCI reader.
 * Events are synchronous timer handles, no module-owned async callbacks. */
typedef Status(EFIAPI *CreateEvent)(uint32_t,uint64_t,void*,void*,void**);
typedef Status(EFIAPI *SetTimer)(void*,uint32_t,uint64_t);
typedef Status(EFIAPI *EventCall)(void*);
typedef Status(EFIAPI *Stall)(uint64_t);
static uint8_t native_pending;
static int dispatch(uint8_t kind,const uint8_t*p,uint32_t n,uint32_t*counter){
 if(kind==1)return active.world(p,n,&front,counter);
 if(kind!=2||native_pending||n>MAX_RUNTIME_BYTES)return 1;
 /* Bytes stay in root-owned file_session until deferred finish. No driver
  * unload occurs while its ATT callback is on the stack. */
 native_pending=1;return 2;
}
static int attach_active(void){return active.attach(system,&file_session);}
static int finish_native(void){
 if(!native_pending)return 0;
 native_pending=0;
 int r=runtime_update(file_session.stream+32,file_session.length-32,0);
 if(fault||r!=4)return 1;
 return rf_finish(&file_session,receipt[2]!=0x21,(uint32_t)policy.counter);
}
static void fatal(void){
 rabbit_supervisor_print_ascii("RADIO OUTCOME UNKNOWN; WATCHDOG RECOVERY\r\n");
 /* Never unload a potentially live driver, never claim OFF. */
 if(guard(5))for(;;)__asm__ volatile("pause");
 for(;;)((Stall)service(system,248))(100000);
}
Status EFIAPI rabbit_connected_run(void*unused,SystemTable*st){
 (void)unused;void*frame_event=0,*deadline=0;uint32_t awaited=0;
 rf_init_owner(&file_session,dispatch);
 if(rabbit_scene_bootstrap(st))return EFI_ERROR(7);
 if(((CreateEvent)service(st,80))(0x80000000u,0,0,0,&frame_event)||
    ((CreateEvent)service(st,80))(0x80000000u,0,0,0,&deadline)||
    ((SetTimer)service(st,88))(frame_event,1,333333)||guard(5)||attach_active())fatal();
 rabbit_supervisor_print_ascii("CONNECTED FILE SERVICE STARTING; ESC TO STOP\r\n");
 for(;;){
  if(guard(5)||active.poll())fatal();
  uint32_t command=active.command();
  if(command!=awaited){
   if(((SetTimer)service(st,88))(deadline,command?2:0,100000000))fatal();
   awaited=command;
  }
  if(awaited&&((EventCall)service(st,120))(deadline)==0)fatal();
  if(native_pending){
   if(finish_native())fatal();
   awaited=0;if(((SetTimer)service(st,88))(deadline,0,0))fatal();
   rabbit_supervisor_print_ascii(file_session.state==RF_APPLIED?
    "OWNER DRIVER COMMITTED; RECEIPT RETAINED FOR RECONNECT\r\n":
    "OWNER DRIVER REJECTED; PREVIOUS WORLD RETAINED\r\n");
  }
  if(((EventCall)service(st,120))(frame_event)==0&&rabbit_scene_tick(st))fatal();
  typedef Status(EFIAPI *ReadKey)(void*,void*);
  uint16_t key[2]={0,0};
  if(system->input&&!((ReadKey)*(void**)((uint8_t*)system->input+8))(system->input,key)&&key[0]==23){
   if(active.close())fatal();
   rabbit_scene_shutdown();
   if(((EventCall)service(st,112))(frame_event)||((EventCall)service(st,112))(deadline))fatal();
   rabbit_supervisor_print_ascii("CONNECTION CLOSED; DRIVER UNLOADED\r\n");return 0;
  }
  if(guard(0))fatal();
  ((Stall)service(st,248))(1000);
 }
}
#ifdef RABBIT_INTEGRATION_TEST
int rabbit_test_connected_boot(SystemTable*st){rf_init_owner(&file_session,dispatch);return rabbit_scene_bootstrap(st)||attach_active();}
int rabbit_test_radio_poll(void){if(guard(5))return 1;int r=active.poll();return guard(0)||r;}
int rabbit_test_control(const uint8_t*p,uint32_t n){return rf_control(&file_session,p,n);}
int rabbit_test_data(const uint8_t*p,uint32_t n){return rf_data(&file_session,p,n);}
void rabbit_test_status(uint8_t*p){rf_status(&file_session,p);}
int rabbit_test_finish(void){return finish_native();}
int rabbit_test_close(void){return active.close();}
#endif
