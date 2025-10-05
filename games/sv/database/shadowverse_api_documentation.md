Shadowverse Card API
===

Basic
---

Every response to all the endpoints is encapsulated in a root JSON object with two keys, a `data_headers` and a `data`. The `data` value is a JSON object. For every endpoint, there exist different keys which contain the actual queried data. In case of any errors, `data` will contain an empty JSON array.

Card information
---

    GET https://shadowverse-portal.com/api/v1/cards

Known Params:

| Parameter  | Possible Values | Comments |
| ------------- | ------------- | ------------- |
| `format`  | json  | required |
| `lang` | two letter language code | Only supports languages that Shadowverse supports. Applies on description and lore. |
| `clan` | 0 through 7 | Filter by craft. <br> 0 = Neutral <br> 1 through 7 = Forest through Haven, in order. |

Response:

`data` key: `cards`

| Key | Type | Comments |
| ------------- | ------------- | ------------- |
| `card_id` |  int | The card ID. <br> Link pages on shadowverse-portal (`https://shadowverse-portal.com/card/{card_id}`) <br> Image link, base (`https://shadowverse-portal.com/image/card/en/C_{card_id}.png`) <br> Image link, evolved (`https://shadowverse-portal.com/image/card/en/E_{card_id}.png`) |
| `foil_card_id` |  int | Unused/unknown usage |
| `card_set_id` |  int | The pack the card belongs to. <br> 10000 = Basic <br> 10001 = Standard <br> 10002 = Darkness Evolved <br> 10003 = Rise of Bahamut <br> 10004 = Tempest of the Gods <br> 90000 = Only obtained during a match (e.g. Thorn Burst, which is only obtainable from Rose Queen's ability) |
| `card_name` |  string | The card name. |
| `is_foil` | int, always 0 | Unused/unknown usage |
| `char_type` |  int | Type of the card. <br> 1 = Follower <br> 2 = Amulet <br> 3 = Countdown Amulet <br> 4 = Spell |
| `clan` | int | Craft the card belongs to. <br> 0 = Neutral <br> 1 through 7 = Forest through Haven, in order. |
| `tribe_name` | string | Trait of the card. For Swordcraft it can be either "Commander" or "Officer", for all other classes it returns "-" |
| `skill_disc` | string | Skill description in plaintext. |
| `evo_skill_disc` | string | Evolved skill description in plaintext. |
| `cost` | int | PP cost of the card. |
| `atk` | int | Attack power of the card. |
| `life` | int | Health of the card. |
| `evo_atk` | int | Attack power of the card after evolution. |
| `evo_life` | int | Health of the card after evolution. |
| `rarity` | int | Rarity. Values are 1 through 4 for Bronze upto Legendary. |
| `get_red_ether` | int | Vials gained upon liquefying. |
| `use_red_ether` | int | Vials required for crafting. |
| `description` | string | Lore of the card. |
| `evo_description` | string | Evolved lore of the card. |
| `cv` | string | card's voice actor.<br/>The string has values only when `lang` is set to `ja`; for everything else the value is `""`. |
| `base_card_id` | int | ID of the original card in case of alternate art version. <br> e.g. Ancient Elf original and alt art have different `card_id`, but same `base_card_id`. |
| `tokens` | always null | Unused/unknown usage? |
| `normal_card_id` | int, same value as card_id | Unused/unknown usage? |

Deck Code
----

    GET https://shadowverse-portal.com/api/v1/deck/import

Known Params:

| Parameter  | Possible Values | Comments |
| ------------- | ------------- | ------------- |
| `format` | json  | required |
| `deck_code` | 4 letter deck code | The deck code. |

Response:

`data` is the root object

| Key | Type | Comments |
| ------------- | ------------- | ------------- |
| `text` | string | Value is always "デッキのインポートに成功しました。" regardless of whether deck code was valid or not. |
| `clan` | string | Craft of the deck. <br> "0" = Neutral <br> "1" through "7" = Forest through Haven, in order. <br> null = error |
| `hash` | string | Hash of the deck. Can be used to <br>- form a deck url: `https://shadowverse-portal.com/deck/{hash}` <br>- form a deck image url: `https://shadowverse-portal.com/image/{hash}` <br>- used to fetch the deck contents using the Fetching Deck from Deck Code endpoint below. <br>This usually does not expire. <br> Key does not exist in case of error. |
| `errors` | array | contains only one json object, with an error key and the error message. <br> Array is empty if no errors occurred. |

Fetching Deck from Deck Code
---

    GET https://shadowverse-portal.com/api/v1/deck

Known Params:

| Parameter  | Possible Values | Comments |
| ------------- | ------------- | ------------- |
| `format`  | json  | required |
| `lang` | two letter language code | Only supports languages that Shadowverse supports. Applies on description and lore. |
| `hash` | hash value from the Deck Code endpoint | Hash of the deck. |

Response:

`data` key: `deck`

| Key | Type | Comments |
| ------------- | ------------- | ------------- |
| `deck_format` | int | Unused/unknown usage? |
| `clan` | int | Craft of the deck. <br> 1 through 7 = Forest through Haven, in order. |
| `cards` | array | Array of the cards used. <br> See response of Card Information endpoint. |