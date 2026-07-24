// ko_dict.js — Korean translation skin for Lost Kingdom.
//
// IMPORTANT: this does NOT translate the Aheui/Brainfuck program. The game
// still computes every response in English internally. This is a DISPLAY
// LAYER: the console buffers each chunk of the game's output and, when it
// recognizes a known English phrase, prints the Korean equivalent instead.
// Phrases were harvested by actually playing the game (see crawl.js).
//
// Matching is longest-first on whole lines / blocks, so partial overlaps
// (e.g. the two "stick of dynamite" variants) resolve correctly.

const KO_DICT = {
  // ── titles / headers ──────────────────────────────────────────────
  "Lost Kingdom": "잃어버린 왕국",
  "Ramshackle Hut": "낡은 오두막",
  "Dirt Patch": "흙밭",
  "Stagnant Pond": "고인 연못",
  "Dirt Path North": "북쪽 흙길",
  "Dirt Path South": "남쪽 흙길",
  "High Plateau": "높은 고원",
  "Forest": "숲",

  // ── room descriptions (matched as whole blocks) ───────────────────
  "You are standing inside your ramshackle wooden hut. The squalor here has\nreplaced the comfort and grandeur of your former royal palace. In one corner\nnear the north door leading to your garden lies the pile of straw you use as\na bed. Fixed in place by an unknown magic, next to a small table, is a wooden\nmockery of your former throne. The main door to the east leads outside to a\nroad.":
    "당신은 낡은 나무 오두막 안에 서 있습니다. 이곳의 초라함이 예전 왕궁의\n안락함과 웅장함을 대신하고 있습니다. 정원으로 통하는 북쪽 문 근처 한구석에는\n당신이 침대로 쓰는 짚더미가 놓여 있습니다. 알 수 없는 마법으로 고정된 작은\n탁자 옆에는 예전 왕좌를 흉내 낸 나무 의자가 있습니다. 동쪽의 정문은 바깥\n길로 이어집니다.",

  "This patch of dirt and weeds bears no comparison to the lush gardens and\nlawns of your former palace; you know that the dry cracked earth here will\nbear no more fruit. A breeze from the west brings the stagnant odour of a\nonce lively pond.":
    "이 흙과 잡초의 밭은 예전 왕궁의 무성한 정원과 잔디밭에 비할 바가 못 됩니다.\n이 메마르고 갈라진 땅에서는 더 이상 열매가 맺히지 않으리란 걸 당신은 압니다.\n서쪽에서 불어오는 바람이 한때 생기 넘치던 연못의 고인 냄새를 실어 옵니다.",

  "The yard continues to a small area containing only a stagnant pool of water.\nThis pond, once teeming with life, is now a mess of brown sludge and green\nalgae. In the distance across the farm of your neighbour you can see a small\nvillage.":
    "마당은 고인 물웅덩이만 있는 작은 구역으로 이어집니다. 한때 생명으로 넘치던\n이 연못은 이제 갈색 진흙과 초록 이끼로 엉망이 되었습니다. 이웃의 농장 너머\n멀리 작은 마을이 보입니다.",

  "You are standing on a dirt path running north-south carved out of the rock by\nmillennia of foot traffic. To the west is the squalid hut that you call home.\nThe sheer cliff face of a mountain range lies to the east and continues into\nthe distance. The path leads north up a steep slope to a high plateau and\ndownhill to a small forest.":
    "당신은 수천 년의 발길에 바위가 깎여 만들어진 남북으로 난 흙길 위에 서\n있습니다. 서쪽에는 당신이 집이라 부르는 초라한 오두막이 있습니다. 동쪽에는\n산맥의 깎아지른 절벽이 멀리까지 이어집니다. 길은 북쪽으로 가파른 비탈을\n올라 높은 고원으로, 아래로는 작은 숲으로 이어집니다.",

  "You are standing at a junction. The path north continues along the sheer\ncliff and leads to a high plateau. Directly south you can see the tangled\ntrees and vines of a small forest. In the distance, to the west, you can see\nthe small village that you now call home.":
    "당신은 갈림길에 서 있습니다. 북쪽 길은 깎아지른 절벽을 따라 이어져 높은\n고원으로 향합니다. 바로 남쪽으로는 작은 숲의 얽힌 나무와 덩굴이 보입니다.\n서쪽 멀리에는 이제 당신의 터전이 된 작은 마을이 보입니다.",

  "You climb a long steep hill up to a high plateau overlooking the mountain\nrange. Surveying the view you can see your ramshackle hut, a small forest and\nin the distance to the west a small village. A dirt path leads down to the\nsouth and to your east you can see the mouth of a cave carved into the\nrock. A strong breeze blows here. The entrance to the cave has been blocked\nby a recent rock fall.":
    "당신은 길고 가파른 언덕을 올라 산맥이 내려다보이는 높은 고원에 이릅니다.\n경치를 둘러보니 낡은 오두막과 작은 숲, 그리고 서쪽 멀리 작은 마을이\n보입니다. 흙길이 남쪽으로 내려가고, 동쪽으로는 바위를 깎아 만든 동굴 입구가\n보입니다. 이곳에는 강한 바람이 붑니다. 동굴 입구는 최근의 낙석으로 막혀\n있습니다.",

  "Vines laced between dense tree growth filter the meagre light shining through\nthe canopy above you. A carpet of soft green moss covers the ground.":
    "빽빽한 나무 사이로 얽힌 덩굴이 머리 위 우거진 잎사귀를 뚫고 들어오는\n희미한 빛을 걸러냅니다. 부드러운 초록 이끼가 양탄자처럼 바닥을 덮고 있습니다.",

  // ── object listings ───────────────────────────────────────────────
  "You can see:": "보이는 것:",
  "a small wooden box of matches sitting on the table (2)":
    "탁자 위에 놓인 작은 나무 성냥갑 (2)",
  "a rusty old lamp lying discarded on the ground (1)":
    "땅에 버려진 녹슨 낡은 램프 (1)",
  "the body of a dead fish, in the reeds around the pond (5)":
    "연못가 갈대밭에 있는 죽은 물고기의 사체 (5)",
  "a stick of dynamite concealed in the hollow of an old tree (3)":
    "오래된 나무 구멍에 숨겨진 다이너마이트 한 개 (3)",
  "a stick of dynamite (3)": "다이너마이트 한 개 (3)",
  "a wooden-handled axe propped up against the stump of a tree (4)":
    "나무 그루터기에 기대어 놓인 나무 손잡이 도끼 (4)",

  // ── inventory / examine ───────────────────────────────────────────
  "You are carrying:": "당신이 지니고 있는 것:",
  "  nothing.": "  아무것도 없음.",
  "a red herring (5)": "훈제 청어 (5)",   // yes -- literally a red herring
  "It is a small box of matches.": "작은 성냥갑입니다.",

  // ── action feedback ───────────────────────────────────────────────
  "Taken.": "집었습니다.",
  "Dropped.": "내려놓았습니다.",
  "Hurled.": "던졌습니다.",
  "You can't go that way.": "그쪽으로는 갈 수 없습니다.",
  "I didn't understand that.": "무슨 말인지 이해하지 못했습니다.",
  "Travelling into the village will not help you in your quest.":
    "마을로 가는 것은 당신의 여정에 도움이 되지 않습니다.",

  // ── death: the red herring ────────────────────────────────────────
  "Yeugh, rotten fish does not taste good...\n\nFrankly, it's poisonous.":
    "우웩, 썩은 생선은 맛이 없군요...\n\n솔직히 말하면, 독이 있습니다.",
  "*** You have died ***": "*** 당신은 죽었습니다 ***",
  "You scored 0 points out of a possible 100.":
    "당신은 가능한 100점 중 0점을 얻었습니다.",
  "You have earned the rank of Amateur.": "당신은 아마추어 등급을 얻었습니다.",
  "  Doing nothing significant. (0 points)": "  이렇다 할 일을 하지 않음. (0점)",

  // ── prompts / meta ────────────────────────────────────────────────
  "To read the back-story enter '!'.": "뒷이야기를 읽으려면 '!'를 입력하세요.",
  "For a list of commands enter '?'.": "명령어 목록을 보려면 '?'를 입력하세요.",
  "Enable long room descriptions (Y/N) ? ":
    "긴 방 설명을 켤까요 (Y/N)? ",
  "Another game (Y/N) ? ": "다시 하시겠습니까 (Y/N)? ",
  "Thanks for playing.": "플레이해 주셔서 감사합니다.",
  "Brainfuck Edition v0.11": "브레인퍽 에디션 v0.11",
  "Brainfuck Edition": "브레인퍽 에디션",

  // ── help headers (kept short; bodies stay English) ────────────────
  "Further Information": "추가 정보",
  "The Parser": "파서",
  "The Classic Nature of This Game": "이 게임의 고전적 성격",
  "Contact Information": "연락처 정보",
  "Credits": "제작진",
  "Supported commands are:": "지원되는 명령어:",
};

if (typeof module !== 'undefined') module.exports = { KO_DICT };
