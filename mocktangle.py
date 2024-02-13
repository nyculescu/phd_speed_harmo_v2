import json

class SmartContract:
    def __init__(self, conditions, action):
        """
        Initializes a smart contract with specific conditions and an action to be executed.

        Parameters:
        - conditions: A callable that takes transaction data as input and returns True if the action should be executed.
        - action: A callable that defines the action to be executed when conditions are met.
        """
        self.conditions = conditions
        self.action = action

    def evaluate_and_execute(self, transaction_data):
        """
        Evaluates the transaction data against the contract's conditions and executes the action if conditions are met.

        Parameters:
        - transaction_data: The data associated with a transaction to be evaluated.
        """
        if self.conditions(transaction_data):
            self.action(transaction_data)

class MockTangle:
    def __init__(self, ledger_file_path):
        """
        Initializes the mock Tangle with a specified ledger file path.

        Parameters:
        - ledger_file_path: Path to the ledger file storing transactions.
        """
        self.ledger_file_path = ledger_file_path
        self.transactions = self.load_ledger()
        self.smart_contracts = []  # List to hold deployed smart contracts

    def load_ledger(self):
        """
        Loads transactions from a ledger file, or initializes a new ledger if the file is not found.

        Returns:
        - A list of transactions loaded from the ledger.
        """
        try:
            with open(self.ledger_file_path, 'r') as file:
                ledger = json.load(file)
            return ledger.get("transactions", [])
        except FileNotFoundError:
            print(f"Ledger file {self.ledger_file_path} not found. Creating a new ledger.")
            return self.initialize_ledger()

    def initialize_ledger(self):
        """
        Initializes a new ledger with a genesis transaction.

        Returns:
        - A list containing the genesis transaction.
        """
        genesis_transaction = {"hash": "genesis", "approving_transactions": [], "data": {"message": "Genesis transaction"}}
        self.save_ledger([genesis_transaction])
        return [genesis_transaction]

    def add_transaction(self, data, approving_transactions):
        """
        Adds a new transaction to the ledger and executes any applicable smart contracts.

        Parameters:
        - data: The data associated with the new transaction.
        - approving_transactions: A list of transactions that this transaction approves.

        Returns:
        - The hash of the added transaction.
        """
        transaction_hash = f"tx_{len(self.transactions)}"
        new_transaction = {"hash": transaction_hash, "approving_transactions": approving_transactions, "data": data}
        self.transactions.append(new_transaction)
        for contract in self.smart_contracts:
            contract.evaluate_and_execute(data)
        self.save_ledger()
        return transaction_hash

    def save_ledger(self):
        """
        Saves the current state of transactions to the ledger file.
        """
        with open(self.ledger_file_path, 'w') as file:
            json.dump({"transactions": self.transactions}, file, indent=4)
    
    def add_smart_contract(self, smart_contract):
        """
        Adds a smart contract to the list of contracts to be evaluated for each transaction.

        Parameters:
        - smart_contract: An instance of SmartContract to be added.
        """
        self.smart_contracts.append(smart_contract)

    def get_recent_transactions(self):
        """
        Retrieves hashes of the two most recent transactions for approval.

        Returns:
        - A list containing hashes of the two most recent transactions.
        """
        return [tx["hash"] for tx in self.transactions[-2:]]

    def get_last_loss(self, node_id):
        """
        Retrieves the last recorded loss for a specific node.

        Parameters:
        - node_id: The identifier of the node whose last loss is to be retrieved.

        Returns:
        - The last loss recorded for the node, or None if not found.
        """
        for transaction in reversed(self.transactions):
            if transaction['data'].get('node_id') == node_id:
                return transaction['data'].get('loss')
        return None

    def get_transactions_for_approval(self, node_id, neighbors):
        """
        Selects transactions for a node to approve, prioritizing those added by neighbors.

        Parameters:
        - node_id: The identifier of the node making the approval.
        - neighbors: A list of neighbor node IDs whose transactions should be prioritized.

        Returns:
        - A list of transaction hashes for the node to approve.
        """
        neighbor_transactions = [tx for tx in self.transactions if tx['data'].get("added_by") in neighbors]
        if neighbor_transactions:
            return [tx["hash"] for tx in neighbor_transactions[-2:]]
        else:
            return self.get_recent_transactions()

#######################################################
# NOTE: Since smart contracts are deployed on the blockchain (or Tangle in this case) and are meant 
#       to be executed in a decentralized manner, a single instance in this simulation can represent 
#       a contract that is universally accessible and executable by any node participating in the network

################## Smart Contract 1 ##################
# Instantiate the SmartContract with a wrapper function to include the dynamic check for loss fluctuation
def create_loss_fluctuation_contract(tangle, initial_loss=None):
    # Initialize last_loss with initial_loss to maintain state across calls
    last_loss = {'value': initial_loss}

    def loss_conditions(data):
        """Check if the current loss is fluctuating within 5% of the last loss."""
        current_loss = data.get("loss")
        # Check if last_loss['value'] is not None to ensure it has been set previously
        if last_loss['value'] is None or current_loss is None:
            return False
        fluctuation = abs(current_loss - last_loss['value']) / last_loss['value']
        return fluctuation <= 0.05

    def loss_action(data):
        """Update the transaction message to 'Abnormal Loss' and announce to neighbors."""
        # Modify the message for transactions with abnormal loss fluctuation
        data["message"] = "Abnormal Loss"
        print(f"Abnormal loss detected. Notifying neighbors.")
        # Add a transaction to the tangle for demonstration
        tangle.add_transaction(data, ["genesis"])  # Simplify the approval process for demonstration
        # Update last_loss after acting on the current loss
        last_loss['value'] = data.get("loss")

    # Return a SmartContract instance with the wrapped condition and action
    return SmartContract(loss_conditions, loss_action)


################## Smart Contract 2 ##################
def significant_environment_change_conditions(last_env_data, current_env_data):
    threshold = 50
    """Check for significant changes in environmental conditions."""
    # Placeholder for actual comparison logic
    # For demonstration, let's assume a simple threshold check
    change_detected = abs(current_env_data - last_env_data) > threshold
    return change_detected

def significant_environment_change_action(data, tangle, node_id, neighbors):
    """Take action on significant environmental changes."""
    print(f"Significant environmental change detected by Node {node_id}.")
    # Here, you could log the event, notify neighbors, or take corrective actions
    # For demonstration, add a transaction to the tangle
    tangle.add_transaction(data, ["genesis"])

def create_significant_environment_change_contract(tangle, initial_env_data=None):
    last_env_data = {'value': initial_env_data}

    def wrapped_conditions(data):
        return significant_environment_change_conditions(last_env_data['value'], data.get("env_data", 0))

    def wrapped_action(data):
        last_env_data['value'] = data.get("env_data", 0)
        significant_environment_change_action(data, tangle, data.get("node_id"), data.get("neighbors", []))

    return SmartContract(wrapped_conditions, wrapped_action)

#######################################################
def test_tangle(mocked_tangle):
    # Tangle, each new transaction approves two previous ones, 
    # contributing to the network's consensus and overall security. 
    # This process ensures that the network remains secure and transactions are verified quickly.

    # Adding a transaction that approves the genesis transaction
    tx1_data = "Transaction 1"
    approving_txs = [mocked_tangle.genesis_transaction, mocked_tangle.genesis_transaction]  # Approving genesis twice for example
    tx1_hash = mocked_tangle.add_transaction(tx1_data, approving_txs)

    # Adding another transaction, this time choosing two transactions to approve
    tx2_data = "Transaction 2"
    approving_txs = mocked_tangle.choose_transactions_to_approve()
    tx2_hash = mocked_tangle.add_transaction(tx2_data, approving_txs)

    print("Tangle Transactions:", mocked_tangle.transactions)

def test_smart_contracts(mocked_tangle):
    tx_data = "Transaction with smart contract"
    approving_txs = mocked_tangle.choose_transactions_to_approve()
    tx_hash = mocked_tangle.add_transaction(tx_data, approving_txs)
    mocked_tangle.execute_smart_contracts(tx_hash)

