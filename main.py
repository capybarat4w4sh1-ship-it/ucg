import streamlit as st
import streamlit.components.v1 as components
import random
import time

# --- 1. スタイル設定 ---
st.set_page_config(page_title="UCG: OC-GOAT!", layout="wide")
st.markdown("""
    <style>
    .card-box {
        border: 2px solid #555; border-radius: 8px 8px 0 0; padding: 10px; text-align: center;
        background: linear-gradient(145deg, #2c3e50, #1a252f); color: white;
        min-height: 220px; display: flex; flex-direction: column; justify-content: space-between;
        transform-style: preserve-3d;
    }
    .field-card { border: 3px solid #f1c40f !important; box-shadow: 0 0 20px rgba(241, 196, 15, 0.7); }
    .p-val { font-size: 2em; font-weight: 900; color: #f1c40f; text-shadow: 1px 1px 2px black; }
    .skill-text { font-size: 0.75em; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 4px; min-height: 60px; }
    .enemy-back {
        width: 40px; height: 60px; background: repeating-linear-gradient(45deg, #222, #222 5px, #444 5px, #444 10px);
        border: 2px solid #888; border-radius: 4px; display: inline-block; margin-right: 2px;
    }
    .timeline-event { margin-bottom: 8px; padding: 10px; background: #1e1e1e; border-radius: 5px; border-left: 4px solid #f39c12; animation: fadeIn 0.5s forwards; opacity: 0; }
    
    @keyframes fadeIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes slideSet {
        0% { transform: translateY(150px) scale(0.8); opacity: 0; }
        100% { transform: translateY(0) scale(1); opacity: 1; }
    }
    @keyframes flipCard {
        0% { transform: perspective(600px) rotateY(90deg); }
        100% { transform: perspective(600px) rotateY(0deg); }
    }
    @keyframes rollDice {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.3); }
        100% { transform: rotate(360deg) scale(1); }
    }
    .dice-container {
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: rgba(0,0,0,0.9); padding: 20px 40px; border-radius: 15px; border: 3px solid #f39c12;
        z-index: 2000; text-align: center; color: white;
        box-shadow: 0 0 50px rgba(0,0,0,0.8);
        display: flex; align-items: center; justify-content: center; gap: 30px;
    }
    .dice-icon { font-size: 3em; animation: rollDice 0.4s ease-in-out infinite; }
    .anim-set { animation: slideSet 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
    .anim-flip { animation: flipCard 0.6s ease-out forwards; }
    .flipped-static { transform: perspective(600px) rotateY(0deg); }
    </style>
""", unsafe_allow_html=True)

# --- 音楽再生ヘルパー ---
if "se_to_play" in st.session_state:
    st.markdown(f'<audio src="{st.session_state.se_to_play}" autoplay style="display:none;"></audio>', unsafe_allow_html=True)
    del st.session_state.se_to_play

def play_se(filename):
    st.session_state.se_to_play = filename

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "MENU"
bgm_file = "assets/bgm_menu.mp3" if st.session_state.app_mode != "BATTLE" else "assets/bgm_battle.mp3"
st.markdown(f'<audio src="{bgm_file}" autoplay loop style="display:none;"></audio>', unsafe_allow_html=True)

# --- 2. カードデータ ---
CARD_DATA = [
    {"id": 1, "name": "絶対王者の風格", "power": 12, "timing": "結果時", "text": "敗北した場合、その瞬間にゲーム敗北となる。"},
    {"id": 2, "name": "切り込み隊長", "power": 9, "timing": "-", "text": "スキルなし。"},
    {"id": 3, "name": "鉄壁の守護者", "power": 6, "timing": "判定時", "text": "敗北を引き分け（継続）にする。"},
    {"id": 4, "name": "お調子者の変身術", "power": "?", "timing": "公開時", "text": "相手の元のパワーをコピーする。"},
    {"id": 5, "name": "不屈の社畜", "power": 7, "timing": "公開時", "text": "手札1枚破棄でパワーを11にする。"},
    {"id": 6, "name": "天真爛漫な疾走", "power": 6, "timing": "終了時", "text": "勝利時、次のドロー枚数を+1する。"},
    {"id": 7, "name": "ミステリアスな微笑", "power": 5, "timing": "公開時", "text": "お互いのカード（数値とスキル）を入れ替える。"},
    {"id": 8, "name": "癒やしの休息", "power": 4, "timing": "終了時", "text": "敗北時、このカードを手札に戻す。"},
    {"id": 9, "name": "いたずらな子猫", "power": 3, "timing": "公開時", "text": "相手の手札をすべて確認する。"},
    {"id": 10, "name": "大逆転の秘策", "power": 1, "timing": "判定時", "text": "相手のパワーが10以上なら、数値に関わらず勝利する。"},
    {"id": 11, "name": "運命のダイス", "power": "?", "timing": "公開時", "text": "山札の残り枚数が偶数なら11、奇数なら2になる。"},
    {"id": 12, "name": "暴走するバイク", "power": 4, "timing": "終了時", "text": "手札を全て捨て、山札から5枚引き直す。"},
    {"id": 13, "name": "二重人格の仮面", "power": 2, "timing": "公開時", "text": "手札1枚破棄でパワーを12にする。"},
    {"id": 14, "name": "甘い誘惑のプリン", "power": 4, "timing": "結果時", "text": "勝利時、次の相手のターンをスキップ。"},
    {"id": 15, "name": "静かなる弓矢", "power": 5, "timing": "公開時", "text": "相手の手札をランダムに1枚捨てる。"},
    {"id": 16, "name": "鋼のメンテナンス", "power": 5, "timing": "結果時", "text": "敗北時、捨て札からP10以上を回収。"},
    {"id": 17, "name": "不思議な領域", "power": 5, "timing": "判定時", "text": "パワーが低い方を勝者とする。"},
    {"id": 18, "name": "過酷な残業代", "power": 3, "timing": "常時", "text": "自分の捨て札が5枚以上ならパワー12。"},
    {"id": 19, "name": "お洒落な衣装替え", "power": 1, "timing": "特殊", "text": "捨て札から除外して場のP+3。"},
    {"id": 20, "name": "沈黙の猫パンチ", "power": 6, "timing": "公開時", "text": "相手のスキルの発動と効果をすべて無効化する。"},
    {"id": 21, "name": "友情の連携攻撃", "power": 5, "timing": "常時", "text": "手札に別のP5があればパワー10になる。"},
    {"id": 22, "name": "究極のフィーリング", "power": "?", "timing": "公開時", "text": "山札の一番上のパワーをコピー。"},
    {"id": 23, "name": "はま寿司への執念", "power": 7, "timing": "結果時", "text": "勝利時：敵手札破棄 / 敗北時：自手札破棄。"},
    {"id": 24, "name": "2Lアイスの誘惑", "power": 1, "timing": "判定時", "text": "このラウンドを強制的に引き分けにする。"},
    {"id": 25, "name": "エステ籠りの成果", "power": 0, "timing": "公開時", "text": "捨て札のスキルを1つコピーする。"},
    {"id": 26, "name": "とにかく裏リーダー", "power": 4, "timing": "終了時", "text": "次に出す自分のパワーを+3。"},
    {"id": 27, "name": "猫なで声の誘い", "power": 5, "timing": "結果時", "text": "敗北時、相手P10以上なら相手の点を1奪う。"},
    {"id": 28, "name": "凛とした決意", "power": 7, "timing": "判定時", "text": "相手のパワー変動を無視し元の数値で勝負。"},
    {"id": 29, "name": "ゆうがないちげき！", "power": 6, "timing": "判定時", "text": "パワー差が4以上あれば勝利。"},
    {"id": 30, "name": "ぱにゃい！の奇跡", "power": 5, "timing": "公開時", "text": "お互いドローし高い数値ならP13になる。"},
]

class Card:
    def __init__(self, data):
        self.__dict__.update(data)
        self.current_power = 0 if data['power'] == "?" else data['power']
        self.orig_power = self.current_power
        self.is_disabled = False
        self.processed = False

class GameEngine:
    def __init__(self, deck_ids):
        def make_deck(ids): return [Card(next(c for c in CARD_DATA if c['id'] == i)) for i in ids]
        self.p = {"name": "あなた", "score": 0, "hand": [], "deck": make_deck(deck_ids), "trash": [], "set": None, "buff": 0, "draw_b": 0, "skip": False}
        self.c = {"name": "CPU", "score": 0, "hand": [], "deck": make_deck([random.randint(1,30) for _ in range(20)]), "trash": [], "set": None, "buff": 0, "draw_b": 0, "skip": False}
        random.shuffle(self.p['deck']); random.shuffle(self.c['deck'])
        for _ in range(5): self.draw(self.p, initial=True); self.draw(self.c, initial=True)
        self.pool, self.phase, self.timeline = 1, "DRAW", []
        self.show_enemy_hand = False
        self.game_over = False
        self.res_queue = []
        self.res_idx = 0
        self.battle_result = "DRAW"
        self.flip_played = False # フリップ演出済みフラグ

    def draw(self, t, num=1, initial=False):
        for _ in range(num + (0 if initial else t['draw_b'])):
            if not t['deck']:
                self.game_over = True
                self.timeline.append(f"💀 {t['name']}の山札が尽きた！（LO負け）")
                return
            t['hand'].append(t['deck'].pop())
        t['draw_b'] = 0

    def play_card(self, p_idx):
        self.p['set'] = self.p['hand'].pop(p_idx)
        self.p['set'].current_power += self.p['buff']; self.p['buff'] = 0
        c_idx = random.randrange(len(self.c['hand']))
        self.c['set'] = self.c['hand'].pop(c_idx)
        self.c['set'].current_power += self.c['buff']; self.c['buff'] = 0
        self.p['set'].processed = False; self.c['set'].processed = False
        self.flip_played = False # ラウンド開始時にフラグをリセット

# --- UIパーツ ---
def ui_card(card, is_field=False, is_hidden=False, anim_class=""):
    style = f"card-box field-card {anim_class}" if is_field else f"card-box {anim_class}"
    if is_hidden:
        st.markdown(f"""
        <div class="{style}">
            <div style="font-size:3em; margin:20px 0;">？</div>
            <img src="assets/card_back.png" onerror="this.style.display='none'" style="width:100%; max-height:80px; object-fit:contain; margin-bottom:5px;">
            <p style="opacity:0.6;">KEEP OUT</p>
        </div>""", unsafe_allow_html=True)
    else:
        p_str = card.power if (card.power == "?" and card.current_power == card.orig_power) else card.current_power
        st.markdown(f"""
        <div class="{style}">
            <div style="text-align:left;"><small>No.{card.id}</small></div>
            <div style="font-weight:bold;">{card.name}</div>
            <img src="assets/card_{card.id}.png" onerror="this.style.display='none'" style="width:100%; max-height:100px; object-fit:contain; margin-bottom:5px;">
            <div class="p-val">P {p_str}</div>
            <div class="skill-text"><span style="color:#f39c12">[{card.timing}]</span><br>{card.text}</div>
        </div>""", unsafe_allow_html=True)

def draw_main_ui(eng, is_open=False, set_anim=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("👤 あなた", f"{eng.p['score']} pt", f"山札: {len(eng.p['deck'])}枚")
    c2.metric("🎁 キャリー", f"{eng.pool} pt")
    c3.metric("🤖 CPU", f"{eng.c['score']} pt", f"山札: {len(eng.c['deck'])}枚")
    
    if eng.show_enemy_hand:
        h_cols = st.columns(len(eng.c['hand']))
        for i, hc in enumerate(eng.c['hand']):
            with h_cols[i]: ui_card(hc)
    else:
        st.markdown("".join(['<img src="assets/card_back.png" class="enemy-back" onerror="this.className=\'enemy-back\'">' for _ in range(len(eng.c['hand']))]), unsafe_allow_html=True)
    st.divider()
    
    field_anim = ""
    if set_anim: 
        field_anim = "anim-set"
    elif is_open:
        # フリップ演出がまだならアニメーション、済みなら静止
        if eng.flip_played:
            field_anim = "flipped-static"
        else:
            field_anim = "anim-flip"
            eng.flip_played = True
        
    f1, f2 = st.columns(2)
    with f1:
        st.caption("🤖 CPU")
        if eng.c['set']: ui_card(eng.c['set'], is_field=True, is_hidden=not is_open, anim_class=field_anim)
    with f2:
        st.caption("👤 あなた")
        if eng.p['set']: ui_card(eng.p['set'], is_field=True, is_hidden=not is_open, anim_class=field_anim)
    st.divider()

# --- メインロジック ---
if "decks" not in st.session_state:
    st.session_state.decks = {"マイデッキ": list(range(1, 21))}

if st.session_state.app_mode == "MENU":
    st.title("🎮 UCG: OC-GOAT! - メインメニュー")
    if st.button("⚔️ バトルへ行く", use_container_width=True):
        play_se("assets/se_click.mp3")
        st.session_state.app_mode = "BATTLE"; st.rerun()
    if st.button("🛠 デッキ構築", use_container_width=True):
        play_se("assets/se_click.mp3")
        st.session_state.app_mode = "DECK_BUILD"; st.rerun()
    if st.button("📖 ルールガイド", use_container_width=True):
        play_se("assets/se_click.mp3")
        st.session_state.app_mode = "RULES"; st.rerun()

elif st.session_state.app_mode == "RULES":
    if st.sidebar.button("⬅ メメニューに戻る", use_container_width=True):
        play_se("assets/se_click.mp3")
        st.session_state.app_mode = "MENU"; st.rerun()
    st.title("📖 ルールガイド")
    st.markdown("""
    ### 1. ゲームの基本構成
    - **勝利条件**: 先に **5ポイント** を獲得したプレイヤーの勝利。
    - **デッキルール**: 全20枚。
    - **LO負け**: 山札が0枚でドローできない場合、その場で敗北。
    ### 2. ターン進行
    1. **ドロー**: 山札から1枚（スキルにより増加）引く。
    2. **セット**: 手札から1枚裏向きに出す。
    3. **オープン**: セットされたカードを公開し **【公開時】** スキルを順に解決。
    4. **判定**: **【常時】【判定時】** スキル適用。数値の大小を比較。
    5. **結果**: **【結果時】** スコア更新。
    6. **終了**: **【終了時】** スキル適用後、カードを捨て札へ。
    ### 3. 特殊システム
    - **ダイスジャッジ**: 公開時スキルが重複した際、ダイスで優先順位を決める。
    - **キャリー**: 引き分け時、勝利ポイントは次ラウンドへ持ち越される。
    - **墓地発動**: 特定のカードは捨て札にある時に特殊アクションを行える。
    """)

elif st.session_state.app_mode == "DECK_BUILD":
    if st.sidebar.button("⬅ メニューに戻る", use_container_width=True):
        play_se("assets/se_click.mp3")
        st.session_state.app_mode = "MENU"; st.rerun()
    st.title("🛠 デッキ構築")
    edit_target = st.selectbox("デッキ選択", list(st.session_state.decks.keys()))
    if "tmp_deck" not in st.session_state or st.session_state.get('last_edit') != edit_target:
        st.session_state.tmp_deck = list(st.session_state.decks[edit_target]); st.session_state.last_edit = edit_target
    if st.button("💾 保存", type="primary", use_container_width=True):
        if len(st.session_state.tmp_deck) == 20: 
            st.session_state.decks[edit_target] = list(st.session_state.tmp_deck)
            play_se("assets/se_click.mp3"); st.success("保存しました！")
        else: st.error("デッキは20枚ちょうどにしてください。")
    cols = st.columns(4)
    for i, c in enumerate(CARD_DATA):
        with cols[i % 4]:
            with st.container(border=True):
                st.markdown(f"**{c['name']}** (P{c['power']})")
                cnt = st.session_state.tmp_deck.count(c['id'])
                c1, c2, c3 = st.columns(3)
                if c1.button("－", key=f"m{c['id']}") and cnt > 0: st.session_state.tmp_deck.remove(c['id']); st.rerun()
                c2.write(cnt)
                if c3.button("＋", key=f"p{c['id']}") and len(st.session_state.tmp_deck) < 20: st.session_state.tmp_deck.append(c['id']); st.rerun()

elif st.session_state.app_mode == "BATTLE":
    if "engine" not in st.session_state:
        st.title("⚔️ バトル準備")
        use_deck = st.selectbox("使用デッキ", list(st.session_state.decks.keys()))
        if st.button("バトル開始！", type="primary"): 
            play_se("assets/se_start.mp3")
            st.session_state.engine = GameEngine(st.session_state.decks[use_deck]); st.rerun()
        st.stop()

    eng = st.session_state.engine
    with st.sidebar:
        if st.button("⬅ メニューに戻る", use_container_width=True):
            del st.session_state.engine; st.session_state.app_mode = "MENU"; st.rerun()
        st.divider()
        st.write("👗 特殊アクション")
        for i, tc in enumerate(eng.p['trash']):
            if tc.id == 19 and eng.phase == "SELECT":
                if st.button(f"衣装替え(No.{i})発動", key=f"trash19_{i}"):
                    eng.p['trash'].pop(i); eng.p['buff'] += 3
                    eng.timeline.append("👗 【衣装替え】捨て札から除外して次バフ+3！"); st.rerun()
        with st.expander("🪦 墓地を確認", expanded=False):
            all_trash = eng.p['trash'] + eng.c['trash']
            if all_trash:
                labels = [f"[{'自' if j < len(eng.p['trash']) else '敵'}] {tc.name}" for j, tc in enumerate(all_trash)]
                sel = st.selectbox("詳細表示", range(len(labels)), format_func=lambda j: labels[j])
                ui_card(all_trash[sel])
            else: st.write("空です")

    if eng.game_over or eng.p['score'] >= 5 or eng.c['score'] >= 5:
        st.title("🏁 ゲーム終了")
        st.subheader(f"勝者: {'あなた' if eng.p['score'] >= 5 else 'CPU'}")
        if st.button("メニューへ戻る"): 
            play_se("assets/se_click.mp3")
            del st.session_state.engine; st.session_state.app_mode = "MENU"; st.rerun()
        st.stop()

    screen = st.empty()
    with screen.container(): draw_main_ui(eng, is_open=(eng.phase in ["OPEN_AUTO", "RESOLVE_COST", "BATTLE", "RESULT", "CLEANUP"]))

    if eng.phase == "DRAW":
        st.subheader("🖐️ 手札")
        h_cols = st.columns(max(len(eng.p['hand']), 1))
        for i, c in enumerate(eng.p['hand']):
            with h_cols[i]: ui_card(c)
        if eng.p['skip']:
            eng.p['skip'] = False; eng.timeline.append("💤 あなたのターンはスキップされた！"); eng.phase = "SELECT"; st.rerun()
        if st.button("📦 ドローフェイズ開始", use_container_width=True, type="primary"):
            play_se("assets/se_draw.mp3")
            eng.draw(eng.p); eng.draw(eng.c); eng.show_enemy_hand = False
            if not eng.game_over: eng.phase = "SELECT"
            st.rerun()

    elif eng.phase == "SELECT":
        if not hasattr(eng, 'select_start_time'): eng.select_start_time = time.time()
        rem_time = int(120 - (time.time() - eng.select_start_time))
        if rem_time <= 0:
            eng.play_card(random.randrange(len(eng.p['hand']))); del eng.select_start_time; eng.phase = "SET_ANIM"; st.rerun()

        st.markdown(f'<div id="rt-timer" style="font-size:1.5em; color:#f39c12; text-align:center; font-weight:bold;">⏱️ 残り時間: {rem_time}s</div>', unsafe_allow_html=True)
        components.html(f"""<script>
            var timeLeft = {rem_time};
            var timerId = setInterval(function() {{
                var el = window.parent.document.getElementById('rt-timer');
                if (el) {{
                    el.innerText = "⏱️ 残り時間: " + timeLeft + "s";
                    if (timeLeft <= 0) {{ clearInterval(timerId); }}
                    timeLeft--;
                }}
            }}, 1000);
        </script>""", height=0)

        st.subheader("🖐️ カードをセットしてください")
        h_cols = st.columns(len(eng.p['hand']))
        for i, c in enumerate(eng.p['hand']):
            with h_cols[i]:
                ui_card(c)
                if st.button("👆 セット", key=f"s{i}", use_container_width=True): 
                    play_se("assets/se_play.mp3")
                    if hasattr(eng, 'select_start_time'): del eng.select_start_time
                    eng.play_card(i); eng.phase = "SET_ANIM"; st.rerun()

    elif eng.phase == "SET_ANIM":
        with screen.container(): draw_main_ui(eng, set_anim=True)
        time.sleep(0.5); eng.phase = "OPEN_WAIT"; st.rerun()

    elif eng.phase == "OPEN_WAIT":
        if st.button("🔥 オープン！", use_container_width=True, type="primary"):
            eng.res_idx = 0; eng.phase = "OPEN_AUTO"; st.rerun()

    elif eng.phase == "OPEN_AUTO":
        p_timing, c_timing = eng.p['set'].timing, eng.c['set'].timing
        if eng.res_idx == 0 and p_timing == c_timing == "公開時":
            pd, cd = random.randint(1, 6), random.randint(1, 6)
            while pd == cd: pd, cd = random.randint(1, 6), random.randint(1, 6)
            dice_ph = st.empty()
            dice_ph.markdown(f'<div class="dice-container"><div class="dice-item">👤 <br><div class="dice-icon">🎲</div><br>{pd}</div><div style="font-size:1.5em; color:#e74c3c; font-weight:900;">VS</div><div class="dice-item">🤖 <br><div class="dice-icon">🎲</div><br>{cd}</div></div>', unsafe_allow_html=True)
            time.sleep(1.2); dice_ph.empty()
            eng.res_queue = [(eng.p, eng.c), (eng.c, eng.p)] if pd > cd else [(eng.c, eng.p), (eng.p, eng.c)]
        elif eng.res_idx == 0:
            eng.res_queue = [(eng.p, eng.c), (eng.c, eng.p)]

        if eng.res_idx < len(eng.res_queue):
            me, opp = eng.res_queue[eng.res_idx]
            card = me['set']
            if card.timing == "公開時" and not card.is_disabled and not card.processed:
                card.processed = True
                if card.id in [5, 13] and me == eng.p:
                    eng.res_idx += 1; eng.phase = "RESOLVE_COST"; st.rerun()
                elif card.id == 20: 
                    opp['set'].is_disabled = True; eng.timeline.append("🐾 【猫パンチ】敵封印！")
                elif card.id == 9: 
                    eng.show_enemy_hand = True; eng.timeline.append("🐱 【子猫】手札看破！")
                elif card.id == 15:
                    if opp['hand']: opp['trash'].append(opp['hand'].pop(random.randrange(len(opp['hand'])))); eng.timeline.append("🏹 【弓矢】手札破壊！")
                elif card.id in [5, 13]: 
                    if me['hand']: me['trash'].append(me['hand'].pop(0)); card.current_power = 11 if card.id == 5 else 12; eng.timeline.append(f"👔 CPU【{card.name}】P{card.current_power}！")
                elif card.id == 4: card.current_power = opp['set'].orig_power; eng.timeline.append(f"✨ 【変身術】P{card.current_power}コピー！")
                elif card.id == 7: 
                    p_data, c_data = eng.p['set'].__dict__.copy(), eng.c['set'].__dict__.copy()
                    eng.p['set'].__dict__.update(c_data); eng.c['set'].__dict__.update(p_data)
                    eng.timeline.append("🌀 【微笑】カードの能力を入れ替えた！")
                elif card.id == 11: card.current_power = 11 if len(me['deck']) % 2 == 0 else 2; eng.timeline.append(f"🎲 【ダイス】P{card.current_power}！")
                elif card.id == 22:
                    if me['deck']: card.current_power = me['deck'][-1].orig_power; eng.timeline.append(f"✨ 【フィーリング】P{card.current_power}コピー！")
                elif card.id == 25:
                    if me['trash']:
                        source = me['trash'][-1]
                        card.text, card.timing, card.id, card.processed = source.text, source.timing, source.id, False
                        eng.timeline.append(f"💄 【エステ籠り】{source.name}のスキルをコピー！"); st.rerun()
                elif card.id == 30:
                    eng.draw(me); eng.draw(opp)
                    if me['hand'] and me['hand'][-1].orig_power > 8: card.current_power = 13; eng.timeline.append("✨ 【ぱにゃい！】奇跡のP13！")
            eng.res_idx += 1; time.sleep(0.4); st.rerun()
        else: eng.phase = "BATTLE"; st.rerun()

    elif eng.phase == "RESOLVE_COST":
        me, opp = eng.res_queue[eng.res_idx-1]; card = me['set']
        st.warning(f"⚡ 【{card.name}】コスト支払い")
        h_cols = st.columns(len(me['hand']))
        for i, hc in enumerate(me['hand']):
            with h_cols[i]:
                ui_card(hc)
                if st.button("🔥 捨てて強化", key=f"c{i}"):
                    me['trash'].append(me['hand'].pop(i)); card.current_power = 11 if card.id == 5 else 12; eng.phase = "OPEN_AUTO"; st.rerun()
        if st.button("❌ 捨てない"): eng.phase = "OPEN_AUTO"; st.rerun()

    elif eng.phase == "BATTLE":
        for t in [eng.p, eng.c]:
            c = t['set']
            if not c.is_disabled:
                if c.id == 18 and len(t['trash']) >= 5: c.current_power = 12
                if c.id == 21 and any(hc.orig_power == 5 for hc in t['hand']): c.current_power = 10
        p_card, c_card = eng.p['set'], eng.c['set']
        pp = p_card.orig_power if (p_card.id == 28 and not p_card.is_disabled) else p_card.current_power
        cp = c_card.orig_power if (c_card.id == 28 and not c_card.is_disabled) else c_card.current_power
        res = "DRAW"
        if pp > cp: res = "PLAYER"
        elif cp > pp: res = "CPU"
        for me, opp in eng.res_queue:
            c = me['set']
            if c.is_disabled: continue
            if c.id == 3 and ((me == eng.p and res == "CPU") or (me == eng.c and res == "PLAYER")): res = "DRAW"
            elif c.id == 10 and opp['set'].current_power >= 10: res = "PLAYER" if me == eng.p else "CPU"
            elif c.id == 17 and pp != cp: res = "PLAYER" if pp < cp else "CPU"
            elif c.id == 24: res = "DRAW"
            elif c.id == 29 and abs(pp - cp) >= 4: res = "PLAYER" if me == eng.p else "CPU"
        if res == "PLAYER": eng.p['score'] += eng.pool; eng.pool = 1
        elif res == "CPU": eng.c['score'] += eng.pool; eng.pool = 1
        else: eng.pool += 1
        eng.battle_result = res
        for me, opp in eng.res_queue:
            c = me['set']
            if c.is_disabled: continue
            is_win = (me == eng.p and res == "PLAYER") or (me == eng.c and res == "CPU")
            is_lose = (me == eng.p and res == "CPU") or (me == eng.c and res == "PLAYER")
            if c.id == 1 and is_lose: me['score'] = -99
            elif c.id == 14 and is_win: opp['skip'] = True
            elif c.id == 23:
                if is_win and opp['hand']: opp['trash'].append(opp['hand'].pop(0))
                if is_lose and me['hand']: me['trash'].append(me['hand'].pop(0))
            elif c.id == 27 and is_lose and opp['set'].current_power >= 10: me['score'] += 1; opp['score'] -= 1
        play_se("assets/se_damage.mp3"); eng.phase = "RESULT"; st.rerun()

    elif eng.phase == "RESULT":
        st.subheader("📝 バトルレポート")
        report_area = st.container()
        for i, line in enumerate(eng.timeline):
            report_area.markdown(f'<div class="timeline-event" style="animation-delay:{i*0.3}s">{line}</div>', unsafe_allow_html=True)
            time.sleep(0.2)
        if st.button("次ラウンドへ ➡", use_container_width=True, type="primary"):
            res = eng.battle_result
            for me, opp in eng.res_queue:
                c = me['set']
                is_win = (me == eng.p and res == "PLAYER") or (me == eng.c and res == "CPU")
                is_lose = (me == eng.p and res == "CPU") or (me == eng.c and res == "PLAYER")
                if not c.is_disabled:
                    if c.id == 6 and is_win: me['draw_b'] = 1
                    elif c.id == 8 and is_lose: me['hand'].append(c); me['set'] = None
                    elif c.id == 16 and is_lose:
                        targets = [tc for tc in me['trash'] if tc.orig_power >= 10]
                        if targets: me['hand'].append(targets.pop())
                    elif c.id == 26: me['buff'] = 3
                    elif c.id == 12: me['trash'].extend(me['hand']); me['hand'] = []; eng.draw(me, 5)
            for t in [eng.p, eng.c]:
                if t['set']: t['trash'].append(t['set']); t['set'] = None
            eng.phase = "DRAW"; eng.timeline = []; st.rerun()
