#!/usr/bin/env python
"""Test with exact long content"""
import requests
import json

token = 'b1bf242b1c8a2b638e79f0b282599ffafea3faf3'
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

hacker_content = """A hacker is a person skilled in information technology who achieves goals and solves problems by non-standard means. The term has become associated in popular culture with a security hacker – someone with knowledge of bugs or exploits to break into computer systems and access data which would otherwise be inaccessible to them. In a positive connotation, though, hacking can also be utilized by legitimate figures in legal situations. For example, law enforcement agencies sometimes use hacking techniques to collect evidence on criminals and other malicious actors. This could include using anonymity tools (such as a VPN or the dark web) to mask their identities online and pose as criminals.

Hacking can also have a broader sense of any roundabout solution to a problem, or programming and hardware development in general, and hacker culture has spread the term's broader usage to the general public even outside the profession or hobby of electronics (see life hack).

Etymology
The term "hacker" is an agent noun formed from the verb "hack" based on PIE *keg- (hook, tooth), which is also the source of the Russian word kogot "claw".

Definitions
Further information: Security hacker, White hat (computer security), Black hat (computer security), and Grey hat

Hackers working on a Linux laptop with computer disks and repair kits in 2022.
Reflecting the two types of hackers, there are two definitions of the word "hacker":

Originally, hacker simply meant advanced computer technology enthusiast (both hardware and software) and adherent of programming subculture; see hacker culture.
Someone who is able to subvert computer security. If doing so for malicious purposes, the person can also be called a cracker.
Mainstream usage of "hacker" mostly refers to computer criminals, due to the mass media usage of the word since the 1990s. This includes what hacker jargon calls script kiddies, less skilled criminals who rely on tools written by others with very little knowledge about the way they work. This usage has become so predominant that the general public is largely unaware that different meanings exist. Though the self-designation of hobbyists as hackers is generally acknowledged and accepted by computer security hackers, people from the programming subculture consider the computer intrusion related usage incorrect, and emphasize the difference between the two by calling security breakers "crackers" (analogous to a safecracker).

The controversy is usually based on the assertion that the term originally meant someone messing about with something in a positive sense, that is, using playful cleverness to achieve a goal. But then, it is supposed, the meaning of the term shifted over the decades and came to refer to computer criminals.

As the security-related usage has spread more widely, the original meaning has become less known. In popular usage and in the media, "computer intruders" or "computer criminals" is the exclusive meaning of the word. In computer enthusiast and hacker culture, the primary meaning is a complimentary description for a particularly brilliant programmer or technical expert. A large segment of the technical community insist the latter is the correct usage, as in the Jargon File definition.

Sometimes, "hacker" is simply used synonymously with "geek": "A true hacker is not a group person. He's a person who loves to stay up all night, he and the machine in a love-hate relationship... They're kids who tended to be brilliant but not very interested in conventional goals It's a term of derision and also the ultimate compliment."""

data = {
    'topic': 'Hacker',
    'raw_content': hacker_content,
    'target_audience': 'General',  # Did user provide this?
    'tone': 'professional',  # Did user provide this?
    'presentation_title': '',
    'num_slides': None,
    'enable_chunking': False,
    'enable_visuals': True
}

print('Sending data...')
response = requests.post('http://localhost:8000/api/presentations/generate/', json=data, headers=headers)
print(f'Status: {response.status_code}')
if response.status_code != 201:
    print(f'ERROR: {response.text}')
else:
    print('SUCCESS')
