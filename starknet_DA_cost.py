# storage diffs are posted as a uint256 array in the calldata
# - number of cell that encode contract deployments
# for each contract deployment:
#   - contract address
#   - contract hash
#   - number of constructor arguments
#   - ...constructor arguments
# - number of contract with storage updates
# for each of those contracts:
#   - contract address
#   - new nonce + number of storage updates
# for each storage update:
#   - storage key
#   - storage value

import random


state_diffs = [
  5,
  2472939307328371039455977650994226407024607754063562993856224077254594995194,
  1336043477925910602175429627555369551262229712266217887481529642650907574765,
  2,
  955723665991825982403667749532843665052270105995360175183368988948217233556,
  2439272289032330041885427773916021390926903450917097317807468082958581062272,
  5,
  2019172390095051323869047481075102003731246132997057518965927979101413600827,
  18446744073709551617, 5, 102,
  2111158214429736260101797453815341265658516118421387314850625535905115418634,
  2,
  619473939880410191267127038055308002651079521370507951329266275707625062498,
  1471584055184889701471507129567376607666785522455476394130774434754411633091,
  619473939880410191267127038055308002651079521370507951329266275707625062499,
  541081937647750334353499719661793404023294520617957763260656728924567461866,
  2472939307328371039455977650994226407024607754063562993856224077254594995194,
  1,
  955723665991825982403667749532843665052270105995360175183368988948217233556,
  2439272289032330041885427773916021390926903450917097317807468082958581062272,
  3429319713503054399243751728532349500489096444181867640228809233993992987070,
  1, 5, 1110,
  3476138891838001128614704553731964710634238587541803499001822322602421164873,
  6, 59664015286291125586727181187045849528930298741728639958614076589374875456,
  600,
  221246409693049874911156614478125967098431447433028390043893900771521609973,
  400,
  558404273560404778508455254030458021013656352466216690688595011803280448030,
  100,
  558404273560404778508455254030458021013656352466216690688595011803280448031,
  200,
  558404273560404778508455254030458021013656352466216690688595011803280448032,
  300,
  1351148242645005540004162531550805076995747746087542030095186557536641755046,
  500
]

def parse(state_diffs):
    n_contract_deployments_cells = state_diffs[0]
    n_deployed_contracts = parse_deployments(state_diffs[1:n_contract_deployments_cells+1])
    n_slots = parse_slots(state_diffs[n_contract_deployments_cells+1:])
    print("number of deployed contracts: {}".format(n_deployed_contracts))
    print("number of slots modified: {}".format(n_slots))

def parse_deployments(deployments_data, n_contracts=0):
    if not deployments_data:
        return n_contracts
    n_contracts += 1
    print("----- deployed contract {} -----".format(n_contracts))
    contract_address = deployments_data[0]
    print("contract address: {}".format(contract_address))
    contract_hash = deployments_data[1]
    print("contract hash: {}".format(contract_hash))
    n_constructor_arguments = deployments_data[2]
    print("number of constructor arguments: {}".format(n_constructor_arguments))
    constructor_arguments = deployments_data[3:3+n_constructor_arguments]
    print("constructor arguments: {}".format(constructor_arguments))
    print("------------------------------")
    if len(deployments_data) > 3+n_constructor_arguments:
        n_contracts = parse_deployments(deployments_data[3+n_constructor_arguments:], n_contracts)
    return n_contracts

def parse_slots(slots_data):
    n_contracts = slots_data[0]
    print("number of contracts with storage updates: {}".format(n_contracts))
    index = 1
    tot_n_slots = 0
    for c in range(n_contracts):
        print("------ contract diffs {} ------".format(c+1))
        index, n_slots = parse_contract_slots(slots_data, index)
        tot_n_slots += n_slots
    return tot_n_slots

def parse_contract_slots(slots_data, index):
    contract_address = slots_data[index]
    print("contract address: {}".format(contract_address))
    n_slots = parse_n_slots(slots_data[index+1])
    print("number of storage updates: {}".format(n_slots))
    for s in range(n_slots):
        print("slot {} <- {}".format(slots_data[index+2+2*s], slots_data[index+2+2*s+1]))
    print("------------------------------")
    return index+2+2*n_slots, n_slots

def parse_n_slots(encoded_data):
    print("encoded data: {}".format(encoded_data))
    nonce = encoded_data >> 64
    n_slots = encoded_data & 0xffffffffffffffff
    return n_slots

def total_calldata_cost(state_diffs):
    # convert each element to a uint256 and then to a byte array
    state_diffs = [int.to_bytes(x, 32, 'big') for x in state_diffs]
    # print(state_diffs)

    cost_per_zero_byte = 4
    cost_per_non_zero_byte = 16

    state_diffs = [list(x) for x in state_diffs]
    # print(state_diffs)

    # calculate the cost of each element
    costs = []
    for x in state_diffs:
        cost = 0
        for y in x:
            cost += cost_per_zero_byte if y == 0 else cost_per_non_zero_byte
        costs.append(cost)

    # print(costs)
    print("total costs: {}".format(sum(costs)))

parse(state_diffs)
total_calldata_cost(state_diffs)

def build_dummy_state_diffs(n_deployed_contracts, n_contracts_with_diffs, n_slots):
    assert len(n_slots) == n_contracts_with_diffs

    state_diffs = []

    constructor_lengths = [random.randint(1, 5) for _ in range(n_deployed_contracts)]

    # number of cell that decode contract deployments
    state_diffs.append(sum([3 + l for l in constructor_lengths])) # 1 address + 1 hash + 1 n_args + args
    
    for i in range(n_deployed_contracts):
        state_diffs.append(random.randint(0, 2**256-1)) # contract address
        state_diffs.append(random.randint(0, 2**256-1)) # contract hash
        state_diffs.append(constructor_lengths[i]) # number of constructor arguments
        for _ in range(constructor_lengths[i]):
            # 50% chance of a small number, 50% chance of a large number
            if random.randint(0, 1) == 0:
                state_diffs.append(random.randint(0, 100))
            else:
                state_diffs.append(random.randint(0, 2**256-1))
    
    # number of contracts with storage updates
    state_diffs.append(n_contracts_with_diffs)
    for i in range(n_contracts_with_diffs):
        state_diffs.append(random.randint(0, 2**256-1)) # contract address
        state_diffs.append(n_slots[i]) # number of slots
        for _ in range(n_slots[i]):
            state_diffs.append(random.randint(0, 2**256-1))
            # 50% chance of a small number, 50% chance of a large number
            if random.randint(0, 1) == 0:
                state_diffs.append(random.randint(0, 100))
            else:
                state_diffs.append(random.randint(0, 2**256-1))
            
    return state_diffs

dummy_state_diffs = build_dummy_state_diffs(0, 1, [10])
print(dummy_state_diffs)
parse(dummy_state_diffs)
total_calldata_cost(dummy_state_diffs)
