# Signal Backup and Restore

- URL: https://chatgpt.com/c/6a6f2938-0378-83ea-b50b-cc711a8a77ea
- Created: 2026-08-02T11:26:02.142Z

---

> if i get signal secure backups paying, can i backup my entire chat history with a friend and then recover it on my desktop?

I’m checking Signal’s current backup and restore rules, especially whether paid Secure Backups can restore directly to Desktop.

```json
{"system1_search_query":[{"q":"site:support.signal.org Secure Backups restore desktop Signal paid backup chat history"},{"q":"site:signal.org/blog Secure Backups Signal desktop restore"},{"q":"site:support.signal.org Signal Desktop transfer chat history mobile backup"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Clarifying backup limits**

I’m distinguishing full chat text from media and desktop restoration. The backup covers all conversations, but disappearing messages are excluded; restoring to a phone first, then linking desktop, syncs chats while older media may not transfer automatically.

**Clarified backup limits**

**Searched 14 websites**

</details>

**Not directly—but there is a two-step route.**

1. **Restore the Secure Backup onto your phone** during Signal’s setup/registration.
2. Install or reinstall Signal Desktop, link it to the restored phone, and choose **Transfer Message History**. This copies **all chats/text messages** to Desktop, but only the **last 45 days of media and attachments**. citeturn830637view0turn830637view3turn830637view4

A few distinctions:

- Secure Backups cover your **whole Signal message archive**, not a separately selected conversation with one friend.
- The free tier already includes **all text messages** plus 45 days of media.
- The **$1.99/month** tier preserves up to **100 GB of older media**, but that older media still is not all synchronized to a newly linked Desktop—Desktop linking is limited to 45 days of media. citeturn830637view0
- View-once messages and messages due to disappear within 24 hours are excluded. citeturn830637view0
- Signal currently does **not** let you restore a mobile Secure Backup file directly into the Desktop app. Its separate “Desktop Backup” feature works in the opposite direction: Desktop backup → primary Android phone. citeturn830637view1turn830637view4

So: **entire textual conversation on Desktop—yes, after restoring to your phone and relinking. Entire historical photo/video/file collection on Desktop—no, only the latest 45 days transfer automatically.**


---

> are there tools to extract the entire backup froma mobile install, say android. Or like, I backed up everything from my iphone, and I wonder if I can restore it to my android phone or even to my already running desktop signal on linux

I’ll separate what Signal officially supports from what third-party extraction tools can do, including cross-platform restore and Linux Desktop limitations.

```json
{"system1_search_query":[{"q":"site:support.signal.org Signal Secure Backups iPhone Android restore cross platform desktop backup Linux"},{"q":"site:support.signal.org Signal Android backup restore iPhone to Android secure backups"},{"q":"site:github.com Signal Android backup extractor decrypt backup tool 2026"},{"q":"site:github.com signal desktop database decrypt export messages Linux"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Checking backup options**

I’m distinguishing Android on-device backups, live app data, and iPhone Secure Backups. The key issue is whether current extraction tools support the newer backup format; I’ll verify that before recommending a path.

**Checked backup options**

**Searched 13 websites**

</details>

The key distinction is whether your iPhone “backup” is Signal Secure Backups or an Apple iCloud/Finder device backup. Only the former can migrate to Android.

```json
{"system1_search_query":[{"q":"site:github.com/bepaald/signalbackup-tools \"backup-v2\" August 2026"},{"q":"site:github.com/bepaald/signalbackup-tools \"new backup format\" \"signalbackup-tools\""},{"q":"site:github.com signal secure backup extractor backup-v2 decrypt"},{"q":"site:github.com signal backup-v2 decrypt export Signal Secure Backups"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Synthesizing the findings**

I’m separating legacy Android backups, newer on-device formats, Secure Backups, and Desktop linking. The practical answer depends on the source, but existing Desktop history generally can’t be overwritten through a normal import.

**Synthesized the findings**

</details>

```json
{"system1_search_query":[{"q":"site:support.signal.org restore Secure Backup linked devices need relink desktop"},{"q":"site:support.signal.org Signal Secure Backup existing linked desktop relink after restore"},{"q":"site:support.signal.org \"Linked devices only sync after your phone has completed restoring\" relink"},{"q":"site:support.signal.org reinstall Signal phone linked desktop remains linked"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Searched 1 website**

</details>

Yes, but **the backup type determines what is possible**.

| Source | Destination | Result |
|---|---|---|
| Signal Secure Backup from iPhone | Fresh Android installation | **Supported** |
| Apple iCloud/Finder iPhone backup | Android Signal | **Not supported** |
| Signal Secure Backup | Existing Linux Desktop installation | **No direct restore or merge** |
| Android on-device backup | Readable files/HTML | Possible, but tool support depends on backup format |

## iPhone → Android

This works officially **only if you enabled Signal Secure Backups inside Signal** and retained the 64-character recovery key. On the Android phone, Signal must be installed or reinstalled, and the backup must be restored during the initial registration flow using the same phone number. Signal explicitly supports iOS-to-Android Secure Backup restores. citeturn360109view2turn360109view1

An ordinary full iPhone backup made through iCloud, Finder or iTunes does **not** contain Signal message history. citeturn457524view3

Therefore, check the old iPhone under **Signal Settings → Backups**. If Secure Backups were never enabled and the original Signal installation is gone, the Apple backup will not recover those chats.

## Getting the restored history onto Linux Desktop

You cannot feed the Secure Backup directly into Signal Desktop or merge it into an already-running Desktop database.

The supported route is:

1. Restore the Secure Backup onto Android.
2. Preserve anything currently unique to the Linux Desktop.
3. Reinstall Signal Desktop and remove its existing local data—on Linux, Signal documents removing `~/.config/Signal`.
4. Relink it to Android.
5. Choose **Transfer Message History** during linking.

This transfers all chats and text history from the phone, but only the last 45 days of media. Paying for the 100 GB Secure Backup tier does not cause older media to transfer to a newly linked Desktop. citeturn808188search6turn584472view3

There is no supported merge with your existing Linux history. Signal also states that Secure Backup archives cannot currently be merged. citeturn360109view1

Before clearing Linux Desktop, use **Settings → Backups** to create an encrypted Desktop backup and save its separate recovery key. That backup can officially be restored onto an Android phone, but not directly back into Desktop. citeturn584472view5

## Extracting an Android backup

Signal’s Android on-device backups contain all messages and media available when the backup is created. Current backups are encrypted folders and require the recovery key; they are primarily intended for restoration into Signal on Android. citeturn584472view6

For **older Android `.backup` files** protected by a 30-digit passphrase, mature unofficial tools exist:

- `signalbackup-tools` can decrypt and export HTML, text, CSV and XML, extract media, and perform some backup or Desktop-history merging.
- `signal-back` and `signal2html` provide more limited extraction/export workflows.

`signalbackup-tools` is unofficial and warns that Signal database changes can break functionality. citeturn457524view2turn128207search8

For the **new backup-v2 folder format**, support is substantially less mature. The main `signalbackup-tools` support issue remains marked work-in-progress. An experimental `signal-backup-v2-helper` can inspect, decrypt, validate and merge certain local Android/Desktop v2 snapshots, but it was archived on May 20, 2026, was last tested against the May 19 schema, and warns that later Signal changes may break it. It is not a polished full HTML-export solution. citeturn457524view1turn813426view0

## Practical recommendation

Your lowest-risk path is:

**iPhone Signal Secure Backup → fresh Android restore → preserve/export existing Linux history → reinstall Linux Desktop → relink with Transfer Message History.**

If the Linux installation contains old messages that are absent from the iPhone backup, keep a separate Desktop backup or readable export. Combining the two histories inside Signal would require experimental backup-v2 manipulation, with a real risk of producing an unrestorable or incomplete archive.


---

> when i do the iphone secure backup -> fresh android, do I get all the images and stuff ? or only 45 days?

```json
{"system1_search_query":[{"q":"site:support.signal.org Secure Backups 45 days media paid 100 GB restore Android iPhone"},{"q":"site:support.signal.org Signal Secure Backups iOS Android restore media 45 days"}],"response_length":"short"}
```

<details><summary>💭 Thinking</summary>

**Searched 4 websites**

</details>

**With the paid Signal Secure Backups tier, restoring the iPhone backup onto a fresh Android installation restores:**

- All backed-up text messages
- Photos, videos, voice messages, files, and other media **older than 45 days**, up to the paid tier’s **100 GB media limit**
- Recent media as well

So the **45-day restriction does not apply to the paid mobile backup restoration**. It applies to the free Secure Backup tier. citeturn333375search0turn333375search1turn333375search4

Important exceptions:

- View-once media is not backed up.
- Messages scheduled to disappear within 24 hours are not backed up.
- Anything deleted before the backup was created will not return.
- You need the 64-character recovery key and must restore during Android’s initial Signal registration flow. citeturn333375search0turn333375search9

**Separate Linux limitation:** after restoring everything to Android, linking a fresh Signal Desktop installation transfers all chats but only the **last 45 days of media** to Linux. Older media remains accessible on the Android phone, even though it was restored successfully there. citeturn333375search11

