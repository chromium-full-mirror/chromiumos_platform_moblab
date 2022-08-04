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

    REQUIRED_LABELS = ["dut:1", "dut:2", "dut:3"]

    def __init__(self):
        self.service = moblab_service.MoblabService()

    async def _get_duts(self, model, board, pool_name):
        """
        Model   Board     Pool    Label
        Leona   Rammus    P1      dut:1
        Leona   Rammus    P1      dut:2
        Leona   Rammus    P1      dut:3
        Cozmo   Jacuzzi   P1
    
        In this scenario, if Cosmo-Jacuzzi is selected with P1 for pool without checking for model & board match, the Suite will kick off with the 3 Leona-Rammus DUTs.
    
        With the model & board match, the Suite cannot be kicked off. Under the pool field, users will see "Pool: P1 requires 3 DUTs with matching board and model as selected above".        
        """
        def _filters(dut):
            labels = dut.get('labels', None)
            if not labels:
                return False

            pools = set(moblab_service.LabelsParser.extract_pool_from_labels(labels))
            board_from_labels = moblab_service.LabelsParser.extract_build_target_from_labels(labels)
            model_from_labels = moblab_service.LabelsParser.extract_model_from_labels(labels)

            return (dut['enrolled'] is True 
                    and model_from_labels 
                    and model.lower() == model_from_labels.lower() 
                    and board_from_labels 
                    and board.lower() == board_from_labels.lower() 
                    and pool_name in pools)

        duts = await self.service.list_duts()
        duts_in_pool = list(filter(_filters, duts))

        return duts_in_pool

    async def check_setup(self, model, board, pool_name):  
        """
        Tests the moblab's connected DUTs to see if the current
        configuration is valid for storage qual run.
        """

        logging.info("Checking storage qual setup on model: %s, board: %s, pool '%s'" % (model, board, pool_name))

        if not pool_name:
            raise StorageQualCheckError("Storage qualification suite has to be run within a pool.")

        if not model:
            raise StorageQualCheckError("Please select model first.")

        if not board:
            raise StorageQualCheckError("Please select board first.")

        # get the pool of the host this test is running on
        duts_in_pool = await self._get_duts(model, board, pool_name)

        if len(duts_in_pool) < 3:
            raise StorageQualCheckError("Pool: %s requires 3 DUTs with matching board and model as selected above." % pool_name)

        # verify that the pool is set up to run storage qual, with correct
        # number of DUTs and correct labels
        required_duts = set()
        for required_label in self.REQUIRED_LABELS:
            duts_with_label = [
                dut["hostname"]
                for dut in duts_in_pool
                if required_label in [label.lower() for label in dut["labels"]]
            ]
            duts_count = len(duts_with_label)

            if duts_count > 1:
                raise StorageQualCheckError(
                    ("Multiple DUTs %s are assigned label '%s' in pool '%s'")
                    % (duts_with_label, required_label, pool_name)
                )

            if duts_count == 0:
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
