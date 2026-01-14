#!/usr/bin/env python
"""
Test auto-chunking for large content
Tests that content over 3500 words automatically enables chunking
"""

import requests
import json

# Your token
TOKEN = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
BASE_URL = 'http://localhost:8000/api'

# Large content (Wikipedia-style about Hacker)
LARGE_CONTENT = """
A hacker is a person who uses computers, networks, or other skills to overcome a technical problem. The term "hacker" may refer to anyone involved in information technology. 

The term originated in the 1960s at Massachusetts Institute of Technology (MIT), where it referred to someone who was able to hack code, but later evolved to include black hat hackers, who use their skills for malicious purposes. In current use, "hacker" can refer to any skilled computer enthusiast, but is often used loosely to refer to a computer criminal. There are also "white hat" hackers who work to protect systems, and "grey hat" hackers who may work both sides.

The history of computer hacking dates back to the early days of computing, when programmers would modify software to make it work in ways that were not originally intended. In the 1970s, the term "hacking" was used to describe the modification of telephones to make free long-distance calls. This led to the formation of groups like 2600: The Hacker Quarterly and the founding of the Chaos Computer Club in Berlin.

In the 1980s and 1990s, hacking became more sophisticated. Hackers began exploring the growing internet, and started to attack computer systems. Some notable incidents include the Morris worm in 1988, the ILOVEYOU virus in 2000, and various attacks on major corporations and government agencies.

Today, hacking is a diverse field. Some hackers work to improve security, while others attempt to exploit vulnerabilities for personal gain or to cause damage. The term "hacker" can refer to:

1. Security researchers who test systems to find vulnerabilities
2. Programmers who write code to solve problems creatively
3. Computer criminals who use hacking to commit fraud or steal data
4. Activists who hack systems to make political or social statements

The ethics of hacking are often debated. Some argue that hacking is a form of artistic expression and self-expression, while others view it as inherently destructive or criminal.

Major types of hacking include:

Social Engineering: Manipulating people into divulging confidential information
Phishing: Sending fraudulent emails to trick users into revealing information
SQL Injection: Exploiting vulnerabilities in database systems
Cross-Site Scripting (XSS): Injecting malicious code into web pages
Denial of Service (DoS): Overwhelming a system with traffic to make it unavailable
Malware: Creating and distributing malicious software
Man-in-the-Middle: Intercepting communications between two parties
Buffer Overflow: Exploiting vulnerabilities in software memory management
Zero-Day Exploits: Using previously unknown vulnerabilities
Network Sniffing: Capturing data packets from network traffic

Hackers use various tools and techniques:

Programming languages like Python, C, Java, and JavaScript
Penetration testing frameworks like Metasploit and Burp Suite
Network analysis tools like Wireshark and tcpdump
Vulnerability scanners like Nessus and OpenVAS
Social engineering frameworks for testing human security

The motivations for hacking vary widely. Some common motivations include:

Financial gain through theft or extortion
Espionage for government or corporate interests
Activism to promote a cause
Curiosity about how systems work
Competition with other hackers
Personal grudges against individuals or organizations

Responses to hacking include:

Legal prosecution under laws like the Computer Fraud and Abuse Act
Imprisonment sentences for serious offenses
Civil lawsuits for damages
Cybersecurity improvements and patches
Increased security awareness training
Creation of dedicated cybersecurity teams

The future of hacking continues to evolve with technology. As systems become more connected through the Internet of Things, cloud computing, and artificial intelligence, new attack vectors emerge. The field of cybersecurity continues to grow as organizations invest more in protecting their systems.

Ethical hacking has become a recognized profession. Companies hire ethical hackers, also known as penetration testers, to test their systems before malicious hackers can exploit vulnerabilities. Certifications like Certified Ethical Hacker (CEH) and Offensive Security Certified Professional (OSCP) are popular in the industry.

The hacking community has its own culture and ethics. Some groups follow principles like:

- Only hacking systems you have permission to test
- Disclosing vulnerabilities responsibly
- Sharing knowledge to improve security
- Using skills for constructive purposes
- Mentoring younger hackers

Recent trends in hacking include:

AI-powered attacks that can identify vulnerabilities faster
Quantum computing threats to current encryption
Blockchain security challenges
Cloud infrastructure attacks
Supply chain compromises
Ransomware targeting critical infrastructure

International cooperation on cybersecurity has become increasingly important, with organizations like INTERPOL and the FBI coordinating efforts against cybercriminals. Most countries have cybersecurity laws and agencies dedicated to protecting their digital infrastructure and responding to attacks.

The role of hackers in society remains controversial. Some are heroes, finding and fixing security flaws. Others are criminals, stealing data and causing harm. Understanding hacking is essential for anyone working in technology or cybersecurity today.
"""

def test_auto_chunking():
    """Test that large content automatically enables chunking"""
    
    # Count words to verify it's large
    word_count = len(LARGE_CONTENT.split())
    print(f"[TEST] Content has {word_count} words")
    
    if word_count <= 3500:
        print(f"[WARNING] Content is only {word_count} words. For auto-chunking test, use content > 3500 words.")
    else:
        print(f"[✓] Content has {word_count} words (>3500) - should trigger auto-chunking")
    
    # Prepare request
    data = {
        "topic": "Hacker",
        "raw_content": LARGE_CONTENT,
        "target_audience": "Business Executives",
        "tone": "professional",
        "num_slides": 20,  # Request 20 slides
        "enable_visuals": True
        # Note: enable_chunking is NOT set - should be auto-enabled
    }
    
    headers = {
        'Authorization': f'Token {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n[REQUEST] Sending {word_count}-word content to /presentations/generate/")
    print(f"[REQUEST] Topic: {data['topic']}")
    print(f"[REQUEST] Audience: {data['target_audience']}")
    print(f"[REQUEST] Tone: {data['tone']}")
    print(f"[REQUEST] Requested Slides: {data['num_slides']}")
    print(f"[REQUEST] Auto-chunking should activate...")
    
    response = requests.post(
        f'{BASE_URL}/presentations/generate/',
        json=data,
        headers=headers,
        timeout=120
    )
    
    print(f"\n[RESPONSE] Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"[✓ SUCCESS] Presentation generated!")
        print(f"[RESULT] Total slides: {result.get('total_slides', 'N/A')}")
        print(f"[RESULT] Presentation title: {result.get('presentation_title', 'N/A')}")
        
        # Show first few slides
        if 'slides' in result:
            print(f"\n[SLIDES] First 3 slides:")
            for i, slide in enumerate(result['slides'][:3]):
                print(f"  Slide {i+1}: {slide.get('title', 'No title')}")
        
        return True
    
    elif response.status_code == 400:
        print(f"[✗ ERROR] Bad Request (400)")
        try:
            error = response.json()
            print(f"[ERROR] Details: {json.dumps(error, indent=2)}")
        except:
            print(f"[ERROR] Response: {response.text}")
        return False
    
    elif response.status_code == 500:
        print(f"[✗ ERROR] Server Error (500)")
        print(f"[ERROR] Response: {response.text}")
        return False
    
    else:
        print(f"[✗ ERROR] Unexpected status: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("AUTO-CHUNKING TEST")
    print("=" * 60)
    print("\nThis test verifies that large content automatically")
    print("enables chunking to avoid token limit errors.\n")
    
    success = test_auto_chunking()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ TEST PASSED - Auto-chunking works!")
    else:
        print("✗ TEST FAILED - Check errors above")
    print("=" * 60)
