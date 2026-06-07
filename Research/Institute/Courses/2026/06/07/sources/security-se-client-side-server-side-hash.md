So if I got this right from my intense research, the following procedure would be preferrable:

Use the PBKDF2 key derivation function to derive a secret key from the users password on the client side.

Use the derived key, which was generated using PBKDF2 and hash that key with Argon2id on the server side, and store 
that hash in the database.

What I wonder now is, why do people typically recommend the key derivation function for creating some secret from a 
password? Could I not just use Argon2id on the client side to hash the password, then pass that hash to the server, and 
then hash that hash again with Argon2id to generate the final hash for the database?

What is so special about this key derivation? And can I not use Argon2 to derive a secret key as well, similar to 
PBKDF2?

2

There's nothing special about PBKDF2. It can -- and should -- be replaced with more modern algorithms like Argon2 
whenever possible. PBKDF2 is not resistant against brute-force attacks with GPUs and specialized hardware (ASICs).

However, unlike Argon2, [PKBDF2 is standardized in the W3C Web Cryptography 
API](https://www.w3.org/TR/WebCryptoAPI/#pbkdf2) and [implemented in 
browsers](https://developer.mozilla.org/en-US/docs/Web/API/Pbkdf2Params). For Argon2, there doesn't even seem to be a 
canonical JavaScript or WebAssembly library, only a couple of GitHub projects which may or may not be production-ready. 
This is a very good reason for preferring PBKDF2 in this specific case.

Note that client-side hashing is a rather exotic feature which only helps in very specific scenarios. First off, from 
the server's perspective, the client-side hash *is* the password. If an attacker can provide the hash, the server will 
happily log them in. It's not necessary to know the original password. So the client-side hashing doesn't protect the 
authentication of your application at all. At best, it protects the password itself, which is only relevant if the 
password has been reused and allows an attacker to gain access to *other* applications as well (which of course should 
never happen). And even then the protection is very limited. If an attacker can exploit vulnerabilities in the 
client-side code, they're likely able to compromise the entire authentication procedure and capture the password before 
it's hashed. If the server is malicious, then nothing prevents it from disabling the client-side hashing. The only 
scenario I can think of is that client-side hashing protects reused(!) passwords in the short window when the server 
has received the password but hasn't hashed it yet.

[edited Sep 5, 2025 at 23:04](https://security.stackexchange.com/posts/274635/revisions "show all edits to this post")

[President James K. Polk](https://security.stackexchange.com/users/662/president-james-k-polk)

254 3 silver badges10 bronze badges

answered Feb 15, 2024 at 13:28

[Ja1024](https://security.stackexchange.com/users/291964/ja1024)

41.6k 2 gold badges99 silver badges127 bronze badges

7

## You must log in to answer this question.

Start asking to get answers

Find the answer to your question by asking.
