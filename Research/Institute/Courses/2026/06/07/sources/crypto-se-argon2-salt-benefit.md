$\begingroup$

I don't understand why I need a salt for Argon2 if Argon2 is only needed as a KDF for a password which is then called 
AES. At the end neither the password nor a password hash is stored. Only the data which was encrypted with the KDF key. 
It is logical that when storing passwords in databases a salt is needed to prevent rainbow table attacks. It is also 
logical that a hard coded salt is bad. But why can't the user password itself be used as salt in case Argon2 is used as 
KDF? (Of course this salt would not be stored with the encrypted data;) ) Maybe I misunderstood the concept of salt... 
[This](https://crypto.stackexchange.com/questions/53032/salt-for-non-stored-passwords) gives me a good overview but it 
can't answer my question directly...

Here is the background: I am creating an app where some user data is stored in a CouchDB database. This data should be 
encrypted locally, as well as in the database. For the prototype, we use symmetric encryption. The procedure is as 
follows:

- The user enters a password.
- the KDF (Argon2id) generates an encryption key from the password and a random salt.
- Using AES-256 GCM, the data set is encrypted with the key and transferred to the cloud.
- on another device the data is downloaded and salt, IV and data are separated.
- Argon2id is then called up again with the salt, the key is generated, and the data is decrypted with it.

The problem: with an increasing number of files, the number of calls to the KDF increases and the performance suffers 
drastically. A single salt would make this much easier.

 $\endgroup$ 1 $\begingroup$

For any sort of password-based key derivation function or password hash, you need the salt to prevent guessing the same 
password across many different users or accounts. In the typical case, verifying the password is by comparing the 
output of the KDF; in this case, verifying the password is by verifying the MAC or AEAD on the encrypted data encrypted 
by that user.

Is it slightly more computationally difficult to do so? Yes. Is it impossible? No. You do definitely need to use a salt 
here, because typically people pick bad passwords and salt makes attacking them substantially more difficult. The only 
time you don't is if you *assign* people random cryptographically secure passwords with sufficient entropy (such as 
tokens) and they use a password manager or other secret store to store them.

However, if you're using the same user account to encrypt many files, you can make this a little more complex to be a 
lot faster. You can use Argon2 with a per-user salt to generate a 512-bit output. Then, you can use a per-file salt and 
the Argon2 output (in place of the secret) as the input to HKDF to generate the key and nonce for AES-GCM to encrypt 
the data. HKDF is very fast, so you can generate the key and nonce for many, many files very quickly.

You could also use something like NaCl's `crypto_box`. Generate a public-private key pair. Use a per-user salt and 
password in Argon2i to generate a key and nonce to encrypt the private key with AES-GCM (or whatever secure algorithm). 
Then, you can encrypt your files with `crypto_box` using the public key, and you only need to use Argon2 to decrypt the 
private key during decryption.

answered Dec 9, 2022 at 23:18

[bk2204](https://crypto.stackexchange.com/users/86107/bk2204)

3,584 8 silver badges12 bronze badges

 $\endgroup$

Start asking to get answers

Find the answer to your question by asking.
