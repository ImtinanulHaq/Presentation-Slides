"""Test 4-8 bullet point requirement with chunked Bitcoin content"""

import sys
import json
sys.path.insert(0, '.')

from presentation_app.presentation_generator import GroqPresentationGenerator

# Bitcoin research paper (3500+ words for chunking)
bitcoin_content = """
Bitcoin is a decentralized digital currency that was introduced in 2009 by an unknown person or group using the pseudonym Satoshi Nakamoto. It operates on a peer-to-peer network without the need for intermediaries like banks. Bitcoin transactions are recorded on a public ledger called the blockchain, which ensures transparency and security through cryptographic mechanisms.

The blockchain is a distributed ledger technology that records all Bitcoin transactions in chronological order. Each block contains a hash of the previous block, creating an immutable chain. Miners validate transactions and add new blocks to the chain by solving complex mathematical puzzles, a process called proof-of-work. This mechanism ensures that no single entity can control the network or manipulate past transactions.

Bitcoin mining is the process of validating transactions and creating new blocks on the blockchain. Miners compete to solve a difficult cryptographic puzzle, and the first to solve it gets to add a new block and receive a reward in the form of newly created bitcoins and transaction fees. The difficulty of these puzzles adjusts automatically to maintain an average block creation time of 10 minutes. Mining requires significant computational power and electricity, making it an economically demanding activity.

The supply of Bitcoin is capped at 21 million coins, making it a deflationary asset. This fixed supply contrasts with traditional currencies, which central banks can print at will, leading to inflation. The creation of new bitcoins follows a predetermined schedule, with the mining reward halving approximately every four years in an event known as the "halving." This schedule is built into Bitcoin's protocol and cannot be changed without consensus from the network participants.

Bitcoin addresses are pseudonymous, meaning transactions can be conducted without revealing the identity of the parties involved. However, Bitcoin transactions are not entirely anonymous since all transactions are visible on the public blockchain. Users can be identified if their addresses are linked to their real-world identities. Wallets store the private keys necessary to access and spend bitcoins. Losing a private key means losing access to the associated bitcoins permanently.

The security of Bitcoin relies on several mechanisms. First, the cryptographic hash function SHA-256 ensures the integrity of transactions and blocks. Second, the proof-of-work consensus mechanism makes it computationally expensive to alter past transactions. Attacking the network would require controlling more than 50% of the network's total computational power, which would be economically infeasible. This security design has proven robust since Bitcoin's inception.

Bitcoin's adoption has grown significantly over the years. Major companies like Tesla, MicroStrategy, and Square have added Bitcoin to their corporate treasuries. Many countries are exploring Bitcoin as a payment option, though regulatory frameworks vary widely. El Salvador officially adopted Bitcoin as legal tender in 2021, becoming the first country to do so. Other nations are considering similar moves or are experimenting with central bank digital currencies.

The price of Bitcoin has experienced significant volatility since its inception. In 2011, Bitcoin reached $1, and by 2017, it peaked above $19,000 before crashing to around $3,500 in 2018. The subsequent bull market saw Bitcoin reach nearly $65,000 in 2021, followed by another correction. Various factors influence Bitcoin's price, including market sentiment, regulatory developments, macroeconomic conditions, and technological innovations.

Bitcoin transactions are immutable once recorded on the blockchain, but transaction fees fluctuate based on network congestion. During periods of high demand, fees can increase substantially, affecting the cost-effectiveness of small transactions. Layer 2 solutions like the Lightning Network have been developed to enable faster, cheaper transactions while maintaining security through periodic settlements on the main blockchain.

The environmental impact of Bitcoin mining has been a subject of considerable debate. Bitcoin mining consumes substantial electrical power, with estimates suggesting it uses as much electricity as entire countries. However, an increasing proportion of mining is powered by renewable energy sources. Some argue that Bitcoin's energy consumption is justified by the security and immutability it provides, while others advocate for energy-efficient alternatives.

Bitcoin has inspired the creation of thousands of alternative cryptocurrencies, collectively known as altcoins. While Bitcoin remains the most well-known and widely adopted cryptocurrency, others like Ethereum have introduced smart contracts, enabling the creation of decentralized applications. The cryptocurrency market has expanded to include various use cases beyond simple peer-to-peer transactions, including decentralized finance and non-fungible tokens.

Regulatory approaches to Bitcoin vary significantly across jurisdictions. Some countries, like El Salvador, have embraced it, while others like China have imposed strict restrictions or bans. Regulatory uncertainty remains a significant challenge for cryptocurrency adoption, as different nations develop different frameworks. International regulatory cooperation is evolving to address issues like money laundering and terrorist financing.

Bitcoin's scalability has been a longstanding challenge. The original blockchain can process approximately 7 transactions per second, far below the capacity of traditional payment systems. Various scaling solutions have been proposed, including the Lightning Network for off-chain transactions and layer 2 solutions. Increasing block size is another proposal, though it involves tradeoffs regarding decentralization and computational requirements.

The concept of digital scarcity, which Bitcoin introduced, has proven revolutionary. By using cryptographic proof-of-work, Bitcoin solved the double-spending problem without requiring a central authority. This innovation has applications beyond cryptocurrency, including in secure digital ownership and supply chain management.

Bitcoin's future remains uncertain and contested. Some view it as digital gold, a store of value for long-term wealth preservation. Others see it as a currency for everyday transactions. Still others argue it is a speculative bubble destined to collapse. Technological developments, regulatory changes, and macroeconomic conditions will likely shape Bitcoin's trajectory in the coming years.
"""

print("\n" + "="*70)
print("TESTING 4-8 BULLET POINT REQUIREMENT")
print("="*70)
print("\nInput: Bitcoin research paper (%d words)" % len(bitcoin_content.split()))
print("Expected: Each slide has 4-8 bullet points\n")

generator = GroqPresentationGenerator(
    topic="Bitcoin and Blockchain Technology",
    raw_content=bitcoin_content,
    target_audience="Technology enthusiasts",
    tone="professional"
)

try:
    result = generator.generate()
    
    # Handle both dict (single generation) and list (chunked array)
    if isinstance(result, dict):
        slides = result.get('slides', [])
    elif isinstance(result, list):
        slides = result
    else:
        raise ValueError("Unexpected result type: %s" % type(result))
    
    print("Generated %d slides\n" % len(slides))
    
    violations = 0
    for i, slide in enumerate(slides, 1):
        bullets = slide.get('bullets', [])
        bullet_count = len(bullets)
        title = slide.get('title', 'Untitled')[:40]
        
        if 4 <= bullet_count <= 8:
            print("[OK] Slide %d: %d bullets" % (i, bullet_count))
        else:
            print("[FAIL] Slide %d: %d bullets (expected 4-8)" % (i, bullet_count))
            violations += 1
    
    print("\n" + "="*70)
    if violations == 0:
        print("SUCCESS: All %d slides have 4-8 bullet points" % len(slides))
    else:
        print("FAILED: %d / %d slides have wrong bullet count" % (violations, len(slides)))
    print("="*70 + "\n")
    
except Exception as e:
    print("ERROR: %s" % str(e))
    import traceback
    traceback.print_exc()
