import logging
import moblab_service


class StorageQualCheckError(Exception):
    pass


class StorageQualCheckService(object):
    """
    Verifies the moblab and DUT setup for storage qual
    A correct setup consists of
        At least one pool (the default "no pool" counts as a pool)
        Each of the labels [retention, trim, suspend] is applied to exactly
            one DUT in the pool.
        No duplication of the labels, all labels are applied exactly once
            per pool
    """

    REQUIRED_LABELS = ["retention", "trim", "suspend"]

    def __init__(self):
        self.service = moblab_service.MoblabService()

    def _get_pool(self, pool_name):
        duts = self.service.list_duts()
        if pool_name is None:
            return duts
        pool = []
        for dut in duts:
            dut_pools = self.service.extract_pool_from_labels(
                dut.get("labels", [])
            )
            if pool_name in dut_pools:
                pool.append(dut)
        return pool

    def check_setup(self, pool_name, variation=0):  # 0 - VARIATION_NOT_SET
        """Tests the moblab's connected DUTs to see if the current
        configuration is valid for storage qual run.
        """

        logging.info("Checking storage qual setup on pool '%s'", pool_name)

        if variation >= 2:  # variation > Variation.REMOVABLE
            # Only regular (VARIATION_NOT_SET) and quick storage quals
            # rely on DUT labels.
            return

        # get the pool of the host this test is running on
        pool = self._get_pool(pool_name)

        # verify that the pool is set up to run storage qual, with correct
        # number of DUTs and correct labels
        required_duts = set()
        for required_label in self.REQUIRED_LABELS:
            duts_with_label = [
                dut["hostname"]
                for dut in pool
                if required_label in [label.lower() for label in dut["labels"]]
            ]

            if len(duts_with_label) > 1:
                raise StorageQualCheckError(
                    ("Multiple DUTs %s are assigned label '%s' in pool '%s'")
                    % (duts_with_label, required_label, pool_name)
                )

            if len(duts_with_label) == 0:
                raise StorageQualCheckError(
                    ("Pool '%s' is missing a DUT with required label '%s'")
                    % (pool_name, required_label)
                )

            if duts_with_label[0] in required_duts:
                raise StorageQualCheckError(
                    (
                        "DUT %s is assigned more than one "
                        "storage qual label (%s) in pool '%s'"
                    )
                    % (
                        duts_with_label[0],
                        str(self.REQUIRED_LABELS),
                        pool_name,
                    )
                )
            required_duts.add(duts_with_label[0])
