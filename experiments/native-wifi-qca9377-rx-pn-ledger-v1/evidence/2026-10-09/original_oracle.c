#include <stdint.h>
#include <stdbool.h>
typedef uint8_t u8;
union htt_rx_pn_t {uint64_t pn48;};
static inline void ccmp_hdr2pn(u8 *pn, u8 *hdr)
{
	pn[0] = hdr[7];
	pn[1] = hdr[6];
	pn[2] = hdr[5];
	pn[3] = hdr[4];
	pn[4] = hdr[1];
	pn[5] = hdr[0];
}
static bool ath10k_htt_rx_pn_cmp48(union htt_rx_pn_t *new_pn,
				   union htt_rx_pn_t *old_pn)
{
	return ((new_pn->pn48 & 0xffffffffffffULL) <=
		(old_pn->pn48 & 0xffffffffffffULL));
}
uint64_t original_iv_pn(uint8_t *iv){u8 p[6];ccmp_hdr2pn(p,iv);uint64_t n=0;for(unsigned j=0;j<6;j++)n=(n<<8)|p[j];return n;}
int original_replay(uint64_t n,uint64_t old){union htt_rx_pn_t a={n},b={old};return ath10k_htt_rx_pn_cmp48(&a,&b);}
