#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t u64;
typedef uint16_t __le16;typedef uint32_t __le32;typedef uint64_t __le64;
#define __packed __attribute__((packed))
#define RX_HTT_HDR_STATUS_LEN 64
#include "rx_desc.h"
struct htt_cmd_hdr {
	u8 msg_type;
} __packed;
struct htt_rx_ring_rx_desc_offsets {
	/* the following offsets are in 4-byte units */
	__le16 mac80211_hdr_offset;
	__le16 msdu_payload_offset;
	__le16 ppdu_start_offset;
	__le16 ppdu_end_offset;
	__le16 mpdu_start_offset;
	__le16 mpdu_end_offset;
	__le16 msdu_start_offset;
	__le16 msdu_end_offset;
	__le16 rx_attention_offset;
	__le16 frag_info_offset;
} __packed;
struct htt_rx_ring_setup_ring32 {
	__le32 fw_idx_shadow_reg_paddr;
	__le32 rx_ring_base_paddr;
	__le16 rx_ring_len; /* in 4-byte words */
	__le16 rx_ring_bufsize; /* rx skb size - in bytes */
	__le16 flags; /* %HTT_RX_RING_FLAGS_ */
	__le16 fw_idx_init_val;

	struct htt_rx_ring_rx_desc_offsets offsets;
} __packed;
struct htt_rx_ring_setup_hdr {
	u8 num_rings; /* supported values: 1, 2 */
	__le16 rsvd0;
} __packed;
struct htt_rx_desc {
	union {
		/* This field is filled on the host using the msdu buffer
		 * from htt_rx_indication
		 */
		struct fw_rx_desc_base fw_desc;
		u32 pad;
	} __packed;
} __packed;
struct htt_rx_desc_v1 {
	struct htt_rx_desc base;
	struct {
		struct rx_attention attention;
		struct rx_frag_info_v1 frag_info;
		struct rx_mpdu_start mpdu_start;
		struct rx_msdu_start_v1 msdu_start;
		struct rx_msdu_end_v1 msdu_end;
		struct rx_mpdu_end mpdu_end;
		struct rx_ppdu_start ppdu_start;
		struct rx_ppdu_end_v1 ppdu_end;
	} __packed;
	u8 rx_hdr_status[RX_HTT_HDR_STATUS_LEN];
	u8 msdu_payload[];
};
int main(void){printf("{\"descriptor_bytes\":%zu,\"payload_bytes\":%zu,\"ring32_bytes\":%zu,\"offsets_words\":[",sizeof(struct htt_rx_desc_v1),sizeof(struct htt_cmd_hdr)+sizeof(struct htt_rx_ring_setup_hdr)+sizeof(struct htt_rx_ring_setup_ring32),sizeof(struct htt_rx_ring_setup_ring32));
printf("%zu",offsetof(struct htt_rx_desc_v1,rx_hdr_status)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,msdu_payload)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,ppdu_start)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,ppdu_end)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,mpdu_start)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,mpdu_end)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,msdu_start)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,msdu_end)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,attention)/4);
printf(",%zu",offsetof(struct htt_rx_desc_v1,frag_info)/4);
printf("]}\n");return 0;}
