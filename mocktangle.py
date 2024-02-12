import json

# tangle class representing a simplified tangle structure for the simulation
# Each transaction directly approves two previous transactions. This helps eliminate the need 
# for miners and achieves faster transaction confirmations as the network grows

class SmartContract:
    def __init__(self, conditions, action):
        """
        Initialize a smart contract with conditions and actions.
        :param conditions: A function that evaluates to True or False, determining if the contract should be executed.
        :param action: The action to be performed when the conditions are met.
        """
        self.conditions = conditions
        self.action = action

    def evaluate_and_execute(self, transaction_data):
        """
        Evaluate the conditions of the smart contract and execute the action if conditions are met.
        :param transaction_data: Data associated with a transaction that might satisfy the contract's conditions.
        """
        if self.conditions(transaction_data):
            self.action(transaction_data)

# Mock Functions: 
# - simulate adding transactions to the Tangle, 
# - choosing transactions to approve, and
# - ensuring data integrity and synchronization across the network.
class MockTangle:
    def __init__(self, ledger_file_path):
        self.ledger_file_path = ledger_file_path
        self.transactions = self.load_ledger()
        self.smart_contracts = []  # List to store smart contracts

    def load_ledger(self):
        """Load transactions from the JSON ledger file."""
        try:
            with open(self.ledger_file_path, 'r') as file:
                ledger = json.load(file)
            return ledger["transactions"]
        except FileNotFoundError:
            print(f"Ledger file {self.ledger_file_path} not found. Creating a new ledger.")
            return self.initialize_ledger()

    def initialize_ledger(self):
        """Create an initial ledger structure with a genesis transaction if the ledger file does not exist."""
        genesis_transaction = {
            "hash": "genesis",
            "approving_transactions": [],
            "data": {"message": "Genesis transaction"}
        }
        # Save the genesis transaction to start the new ledger
        self.save_ledger([genesis_transaction])
        return [genesis_transaction]

    def add_transaction(self, data, approving_transactions):
        transaction_hash = "tx_" + str(len(self.transactions))
        new_transaction = {"hash": transaction_hash, "approving_transactions": approving_transactions, "data": data}
        self.transactions.append(new_transaction)
        # Execute smart contracts with the new transaction data
        for contract in self.smart_contracts:
            contract.evaluate_and_execute(data)
        self.save_ledger()
        return transaction_hash

    def save_ledger(self, transactions=None):
        """Save the updated transactions back to the JSON ledger file."""
        if transactions is None:
            transactions = self.transactions
        with open(self.ledger_file_path, 'w') as file:
            json.dump({"transactions": transactions}, file, indent=4)
    
    def add_smart_contract(self, smart_contract):
        self.smart_contracts.append(smart_contract)

    def get_recent_transactions(self):
        """Fetch two most recent transactions for approval."""
        if len(self.transactions) >= 2:
            return [self.transactions[-1]["hash"], self.transactions[-2]["hash"]]
        elif len(self.transactions) == 1:
            # If only genesis exists, approve it twice
            return ["genesis", "genesis"]
        else:
            # Fallback, should not happen if genesis is properly initialized
            return []
    
    def get_last_loss(self, node_id):
        """Retrieve the last loss value for a specific node from the transactions."""
        for transaction in reversed(self.transactions):
            if transaction['data'].get('node_id') == node_id:
                return transaction['data'].get('loss')
        return None
        
    def get_transactions_for_approval(self, node_id, neighbors):
        """Fetch transactions for approval considering the network topology."""
        # Simplified logic: prioritize transactions added by neighbors, fallback to recent transactions
        neighbor_transactions = [tx for tx in self.transactions if tx.get("added_by") in neighbors]
        if len(neighbor_transactions) >= 2:
            return [neighbor_transactions[-1]["hash"], neighbor_transactions[-2]["hash"]]
        else:
            return self.get_recent_transactions()  # Fallback to recent transactions if not enough neighbor transactions

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
        """Check if the current loss is fluctuating within ±5% of the last loss."""
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

