#ifndef QETH_WMI_GENERATOR_ORACLE
#define QETH_WMI_GENERATOR_ORACLE
#include "primary_wmi.h"
typedef uint32_t u32;struct ath10k {int unused;};struct sk_buff {uint8_t data[64];};struct wmi_tlv {uint16_t len,tag;uint8_t value[];} __packed;
static struct sk_buff*ath10k_wmi_alloc_skb(struct ath10k*a,unsigned n){static struct sk_buff s;(void)a;assert(n<=sizeof s.data);memset(&s,0,sizeof s);return &s;}
#define __cpu_to_le16(x) (x)
#define __cpu_to_le32(x) (x)
#define ERR_PTR(x) ((void*)(intptr_t)(x))
#define ENOMEM 12
#define ath10k_dbg(...) ((void)0)
static struct sk_buff *
ath10k_wmi_tlv_op_gen_vdev_set_param(struct ath10k *ar, u32 vdev_id,
				     u32 param_id, u32 param_value)
{
	struct wmi_vdev_set_param_cmd *cmd;
	struct wmi_tlv *tlv;
	struct sk_buff *skb;

	skb = ath10k_wmi_alloc_skb(ar, sizeof(*tlv) + sizeof(*cmd));
	if (!skb)
		return ERR_PTR(-ENOMEM);

	tlv = (void *)skb->data;
	tlv->tag = __cpu_to_le16(WMI_TLV_TAG_STRUCT_VDEV_SET_PARAM_CMD);
	tlv->len = __cpu_to_le16(sizeof(*cmd));
	cmd = (void *)tlv->value;
	cmd->vdev_id = __cpu_to_le32(vdev_id);
	cmd->param_id = __cpu_to_le32(param_id);
	cmd->param_value = __cpu_to_le32(param_value);

	ath10k_dbg(ar, ATH10K_DBG_WMI, "wmi tlv vdev %d set param %d value 0x%x\n",
		   vdev_id, param_id, param_value);
	return skb;
}

#endif
