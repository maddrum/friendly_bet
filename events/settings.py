# phases

PHASE_GROUP = 'group'
PHASE_EIGHT = 'eight_final'
PHASE_QUARTER = 'quarter_final'
PHASE_SEMI = 'semi_final'
PHASE_LITTLE_FINAL = 'little_final'
PHASE_FINAL = 'final'

PHASE_SELECTOR = [(PHASE_GROUP, 'Групова фаза'),
                  (PHASE_EIGHT, 'Осминафинали'),
                  (PHASE_QUARTER, 'Четвъртфинал'),
                  (PHASE_SEMI, 'Полуфинал'),
                  (PHASE_LITTLE_FINAL, 'Малък финал'),
                  (PHASE_FINAL, 'Финал')]

# match states
MATCH_STATE_HOME = 'home'
MATCH_STATE_GUEST = 'guest'
MATCH_STATE_PENALTIES_HOME = 'penalties_home'
MATCH_STATE_PENALTIES_GUEST = 'penalties_guest'

MATCH_STATES_BASE = [(MATCH_STATE_HOME, 'Победа домакин'),
                     (MATCH_STATE_GUEST, 'Победа гост')]
MATCH_STATES_KNOCKOUTS = [(MATCH_STATE_PENALTIES_HOME, 'Победа за домакин след дузпи'),
                          (MATCH_STATE_PENALTIES_GUEST, 'Победа за гост след дузпи')]

MATCH_STATES = MATCH_STATES_BASE + MATCH_STATES_KNOCKOUTS
