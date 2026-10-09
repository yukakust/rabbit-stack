#ifndef QETH_PRIMARY_HTT
#define QETH_PRIMARY_HTT
#include <stdint.h>
typedef uint8_t u8;typedef uint16_t __le16;typedef uint32_t __le32;
#ifndef __packed
#define __packed __attribute__((packed))
#endif
enum peth_data_tx_desc_flags0 {
	PETH_DATA_TX_DESC_FLAGS0_MAC_HDR_PRESENT = 1 << 0,
	PETH_DATA_TX_DESC_FLAGS0_NO_AGGR         = 1 << 1,
	PETH_DATA_TX_DESC_FLAGS0_NO_ENCRYPT      = 1 << 2,
	PETH_DATA_TX_DESC_FLAGS0_NO_CLASSIFY     = 1 << 3,
	PETH_DATA_TX_DESC_FLAGS0_RSVD0           = 1 << 4
#define PETH_DATA_TX_DESC_FLAGS0_PKT_TYPE_MASK 0xE0
#define PETH_DATA_TX_DESC_FLAGS0_PKT_TYPE_LSB 5
};
enum peth_data_tx_desc_flags1 {
#define PETH_DATA_TX_DESC_FLAGS1_VDEV_ID_BITS 6
#define PETH_DATA_TX_DESC_FLAGS1_VDEV_ID_MASK 0x003F
#define PETH_DATA_TX_DESC_FLAGS1_VDEV_ID_LSB  0
#define PETH_DATA_TX_DESC_FLAGS1_EXT_TID_BITS 5
#define PETH_DATA_TX_DESC_FLAGS1_EXT_TID_MASK 0x07C0
#define PETH_DATA_TX_DESC_FLAGS1_EXT_TID_LSB  6
	PETH_DATA_TX_DESC_FLAGS1_POSTPONED        = 1 << 11,
	PETH_DATA_TX_DESC_FLAGS1_MORE_IN_BATCH    = 1 << 12,
	PETH_DATA_TX_DESC_FLAGS1_CKSUM_L3_OFFLOAD = 1 << 13,
	PETH_DATA_TX_DESC_FLAGS1_CKSUM_L4_OFFLOAD = 1 << 14,
	PETH_DATA_TX_DESC_FLAGS1_TX_COMPLETE      = 1 << 15
};
enum peth_data_tx_ext_tid {
	PETH_DATA_TX_EXT_TID_NON_QOS_MCAST_BCAST = 16,
	PETH_DATA_TX_EXT_TID_MGMT                = 17,
	PETH_DATA_TX_EXT_TID_INVALID             = 31
};
struct peth_data_tx_desc {
	u8 flags0; /* %PETH_DATA_TX_DESC_FLAGS0_ */
	__le16 flags1; /* %PETH_DATA_TX_DESC_FLAGS1_ */
	__le16 len;
	__le16 id;
	__le32 frags_paddr;
	union {
		__le32 peerid;
		struct {
			__le16 peerid;
			__le16 freq;
		} __packed offchan_tx;
	} __packed;
	u8 prefetch[0]; /* start of frame, for FW classification engine */
} __packed;
#endif
