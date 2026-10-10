# Shared label definitions

## Topics

- `access`: login, signup, password, or account access.
- `usability`: navigation, controls, layout, queue/playlist management, or ad interruptions.
- `playback`: playback failure, crashes, lag, connection failures, audio quality, or resource use.
- `downloads`: downloads, saved music, offline listening, or disappearing downloads.
- `catalog`: missing content, search/discovery, recommendations, or lyrics.
- `billing`: price, charges, subscriptions, paywalls, or premium entitlement.
- `support`: contacting support or the support response.
- `other`: general praise/criticism, unrelated content, or no supported specific topic.

Choose the highest-severity supported problem. On a tie, choose the first specific problem mentioned.
For praise, choose the first specifically praised feature. A paid-plan mention alone is not billing.

## Intent

Precedence: `cancellation` -> `complaint` -> `request` -> `praise` -> `unclear`.

## Severity

1. No reported problem, praise, neutral/unclear content, or pure feature request.
2. Dislike, generic criticism, minor annoyance, or cosmetic issue without functional loss.
3. Degraded or restricted function where some use or workaround remains.
4. Clearly blocked core task such as inability to log in or play music.
5. Explicit serious financial, privacy, or data harm.

Cancellation intent, anger, stars, or an expensive plan do not automatically raise severity.

