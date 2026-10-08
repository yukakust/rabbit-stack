#ifndef RABBIT_QCA_PERSISTENT_LIFECYCLE_H
#define RABBIT_QCA_PERSISTENT_LIFECYCLE_H
#include <stdint.h>
enum { QCA_RADIO_ACTIVE=1, QCA_RADIO_QUIESCING, QCA_RADIO_RELEASING,
 QCA_RADIO_CLOSED, QCA_RADIO_RETAINED };
enum { QCA_RADIO_TIMEOUT=1, QCA_RADIO_CLOCK, QCA_RADIO_OWNERS };
/* Trusted adapter supplies fresh observations, not firmware/GATT claims.
 * epoch identifies ONE adapter acquisition, never a packet counter.
 * All booleans must be normalized. stop_verified means every owned CE halted,
 * device IRQ quiesced, PCI bus master off and DMA writes fenced/observed stopped.
 * It does not mean buffers have been unmapped or firmware pin released.
 */
typedef struct {
 uint64_t epoch;
 uint32_t mappings, dma_users;
 uint8_t pci, wake, link, irq, pin, bus, bus_master;
 uint8_t init_ready, stop_verified;
} QcaRadioOwners;
typedef struct {
 QcaRadioOwners owners;
 uint64_t last, deadline;
 uint32_t phase, error;
} QcaRadioLifecycle;
/* Policy only: no MMIO, allocation, release, cryptography or RF commands.
 * Current profile requires exactly14 mappings/dma_users, retained firmware,
 * PCI/wake/link/IRQ/bus owners and a real validated WMI READY. It establishes
 * command admission, NOT station/VDEV, scan, association or IP readiness.
 */
int qca_radio_begin(QcaRadioLifecycle*,const QcaRadioOwners*,uint64_t);
/* Every command must refresh owners first, then consult accepts_work.
 * Failure while active permanently retains ownership until explicit recovery.
 * Malformed/stale observations fail closed to RETAINED, preserving the last
 * owner counts but revoking command and release admission.
 */
int qca_radio_observe(QcaRadioLifecycle*,const QcaRadioOwners*,uint64_t);
int qca_radio_accepts_work(const QcaRadioLifecycle*);
/* Caller must authenticate authorization BEFORE calling this local API.
 * Stops new command admission immediately. Deadline is in caller's monotonic
 * units (microseconds in current adapter), no sleeps inside this module.
 */
int qca_radio_quiesce(QcaRadioLifecycle*,uint64_t,uint64_t);
/* True only after current stop proof; tells caller release MAY be attempted,
 * never that it succeeded. Release failure/timeout cannot grant unload.
 */
int qca_radio_can_release(const QcaRadioLifecycle*);
int qca_radio_can_unload(const QcaRadioLifecycle*);
#endif
