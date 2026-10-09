from pathlib import Path
R=Path(__file__).resolve().parent
def fn(file,name):
 s=(R/'references'/file).read_text();at=s.index(name+'(');start=s.rfind('\n',0,at)+1;brace=s.index('{',at);depth=1;end=brace+1
 while depth:
  depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[start:end]
def oracle():
 return '#include <stdint.h>\n#include <stdbool.h>\ntypedef uint8_t u8;\nunion htt_rx_pn_t {uint64_t pn48;};\n'+fn('mac80211-wpa.c','ccmp_hdr2pn')+'\n'+fn('htt_rx.c','ath10k_htt_rx_pn_cmp48')+'\nuint64_t original_iv_pn(uint8_t *iv){u8 p[6];ccmp_hdr2pn(p,iv);uint64_t n=0;for(unsigned j=0;j<6;j++)n=(n<<8)|p[j];return n;}\nint original_replay(uint64_t n,uint64_t old){union htt_rx_pn_t a={n},b={old};return ath10k_htt_rx_pn_cmp48(&a,&b);}\n'
