import pygame, sys, random, copy
from pygame.locals import *
from cards import *

def genCard(cList, xList):
    #Generate and remove an card from cList and append it to xList.
    #Return the card, and whether the card is an Ace
    cA = 0
    card = random.choice(cList)
    cList.remove(card)
    xList.append(card)
    if card in cardA:
        cA = 1
    return card, cA

def initGame(cList, uList, dList):
    #Generates two cards for dealer and user, one at a time for each.
    #Returns if card is Ace and the total amount of the cards per person.
    userA = 0
    dealA = 0
    card1, cA = genCard(cList, uList)
    userA += cA
    card2, cA = genCard(cList, dList)
    dealA += cA
    dealAFirst = copy.deepcopy(dealA)
    card3, cA = genCard(cList, uList)
    userA += cA
    card4, cA = genCard(cList, dList)
    dealA += cA
    #The values are explained below when calling the function
    return getAmt(card1) + getAmt(card3), userA, getAmt(card2) + getAmt(card4), dealA, getAmt(card2), dealAFirst

def make_state(userSum, userA, dealFirst, dealAFirst):
    #Eliminate duplicated bust cases
    if userSum > 21: 
        userSum = 22
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace   
    return (userSum, userA, dealFirst, dealAFirst)

def simulate_sequence(s, cards_left, user_cards): # simulate sequence for MC policy evaluation
  episode = [s] # episode contains initial state to begin with

  while s[0] < 17: # while sum of user's cards < 17
    nextCard = genCard(cards_left, user_cards)
    s = make_state(s[0] + getAmt(nextCard[0]), s[1] + nextCard[1], s[2], s[3]) # generate next state from randomly drawn card
    episode.append(s) # append to episode

  return episode # return episode of states from initial state to final state

def simulate_one_step(s, cards_left, user_cards): # simulate one step for TD-learning
  if (s[0] >= 17):
    return None # next state is None, current state is the final state
  elif (s[0] < 17): 
    nextCard = genCard(cards_left, user_cards)
    return make_state(s[0] + getAmt(nextCard[0]), s[1] + nextCard[1], s[2], s[3]) # generate next state from randomly drawn card

def reward_to_go(state, deal_sum): # reward to go at terminal state
  if (state[0] > 21): # if user sum is above 21, immediate loss
    return -1
  elif (state[0] <= 21 and deal_sum <= 21 and deal_sum > state[0]): # if dealer sum greater than user's, user loses
    return -1
  elif ( (state[0] <= 21 and deal_sum > 21) or (state[0] <= 21 and deal_sum <= 21 and state[0] > deal_sum) ): # if dealer goes bust or user's sum is greater than dealer's, user wins
    return 1
  else: # else there is a tie
    return 0

def reward(state): # reward calculation for intermediate states
  if (state[0] > 21): # if user sum is above 21, user loses
    return -1
  elif (state[0] == 21): # if user sum is exactly 21, user has won
    return 1
  else: # else, no definitive winner or loser yet
    return 0

def argmax(s, Qvalues):
  if (Qvalues[s][0] > Qvalues[s][1]): # if reward for hitting is better
    return 0
  else: # if reward for standing is better
    return 1

def pick_action(s, epsilon, Qvalues):
  if random.choice([0, 1]) < epsilon: # if random choice is 0
    return random.choice([0, 1]) # randomly pick action
  else: # if random choice is 1
    return argmax(s, Qvalues) # return better action for state s 

def simulate_one_step_Q(s, a, cards_left, user_cards): # simulate one step for Q-learning
  if a == 0: # if action is to hit, find next_s
    nextCard = genCard(cards_left, user_cards)
    return make_state(s[0] + getAmt(nextCard[0]), s[1] + nextCard[1], s[2], s[3])
  elif a == 1: # if action is to stand, next_s is null
    return None

def main():
    ccards = copy.copy(cards)
    stand = False
    userCard = []
    dealCard = []
    winNum = 0
    loseNum = 0
    #Initialize Game
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Blackjack')
    font = pygame.font.SysFont("", 20)
    hitTxt = font.render('Hit', 1, black)
    standTxt = font.render('Stand', 1, black)
    restartTxt = font.render('Restart', 1, black)
    MCTxt = font.render('MC', 1, blue)
    TDTxt = font.render('TD', 1, blue)
    QLTxt = font.render('QL', 1, blue)
    gameoverTxt = font.render('End of Round', 1, white)

    #Prepare table of utilities (expected utilities)
    MCvalues = {}
    TDvalues = {}
    Qvalues = {}
    G = {}
    N_td = {}
    N_q = {}
    #i iterates through the sum of user's cards. It is set to 22 if the user went bust. 
    #a1 is the number of Aces that the user has.
    #j iterates through the value of the dealer's first card. Ace is eleven. 
    #a2 denotes whether the dealer's first card is Ace. 
    for i in range(2,23):
        for j in range(2,12):
            for a1 in range(0,5):
                for a2 in range(0,2):
                    s = (i,a1,j,a2)
                    #utility computed by MC-learning
                    MCvalues[s] = 0
                    G[s] = []
                    # tracks how many times certain states have been visited in TD-learning and Q-learning
                    N_td[s] = 0
                    N_q[s] = 0
                    #utility computed by TD-learning
                    TDvalues[s] = 0
                    #first element is Q value of "Hit", second element is Q value of "Stand"
                    Qvalues[s] = [0,0]
    #userSum: sum of user's cards
    #userA: number of user's Aces
    #dealSum: sum of dealer's cards (including hidden one)
    #dealA: number of all dealer's Aces, 
    #dealFirst: value of dealer's first card
    #dealAFirst: whether dealer's first card is Ace
    userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
    state = make_state(userSum, userA, dealFirst, dealAFirst)
    #Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((80, 150, 15))
    hitB = pygame.draw.rect(background, gray, (10, 445, 75, 25))
    standB = pygame.draw.rect(background, gray, (95, 445, 75, 25))
    MCB = pygame.draw.rect(background, white, (180, 445, 75, 25))
    TDB = pygame.draw.rect(background, white, (265, 445, 75, 25))
    QLB = pygame.draw.rect(background, white, (350, 445, 75, 25))
    autoMC = False
    autoTD = False
    autoQL = False
    #Event loop
    while True:
        #Our state information does not take into account of number of cards
        #So it's ok to ignore the rule of winning if getting 5 cards without going bust
        if (userSum >= 21 and userA == 0) or len(userCard) == 5:
            gameover = True
        else:
            gameover = False
        if len(userCard) == 2 and userSum == 21:
            gameover = True
        if autoMC:
          for i in range(1000):
            # copy initial states
            cards_left = copy.copy(ccards)
            user_cards = copy.copy(userCard)
            dealer_cards = copy.copy(dealCard)

            # random state generation
            vals = initGame(cards_left, user_cards, dealer_cards)
            s = make_state(vals[0], vals[1], vals[4], vals[5])
            deal_sum = vals[2]
            deal_a = vals[3]

            episode = simulate_sequence(s, cards_left, user_cards) # episode simulation

            finalState = episode[len(episode) - 1] # finalState is state of termination in episode

            #simulate dealer's moves from final state to terminal state
            if deal_sum != 21:
              while deal_sum <= finalState[0] and deal_sum < 17:
                next_dealer_card = genCard(cards_left, dealer_cards)

                deal_sum += getAmt(next_dealer_card[0])
                deal_a += next_dealer_card[1]

                while deal_sum > 21 and deal_a > 0:
                  deal_a -= 1
                  deal_sum -= 10

            finalReward = reward_to_go(finalState, deal_sum) # find definitive reward value at terminal state

            # back-propagate final reward
            i = 0
            for each in episode:
              G[s].append(0.9**i * finalReward) # append reward of intermediate state to initial state
              i+=1

            MCvalues[s] = sum(G[s]) / len(G[s]) # find and store average of all rewards in a state

        if autoTD:
          for i in range(1000):
            # copy initial states
            cards_left = copy.copy(ccards)
            user_cards = copy.copy(userCard)
            dealer_cards = copy.copy(dealCard)

            # random state generation
            vals = initGame(cards_left, user_cards, dealer_cards)
            s = make_state(vals[0], vals[1], vals[4], vals[5])
            deal_sum = vals[2]
            deal_a = vals[3]

            while s is not None:
              N_td[s] += 1 # keep track of how many visits to the state

              next_s = simulate_one_step(s, cards_left, user_cards) # find next state from current state

              if next_s is None: # next state null if final state has been reached

                # simulate dealer's moves from final state to terminal state
                if deal_sum != 21:
                  while deal_sum <= s[0] and deal_sum < 17:
                    next_dealer_card = genCard(cards_left, dealer_cards)

                    deal_sum += getAmt(next_dealer_card[0])
                    deal_a += next_dealer_card[1]

                    while deal_sum > 21 and deal_a > 0:
                      deal_a -= 1
                      deal_sum -= 10
                
                TDvalues[s] = reward_to_go(s, deal_sum) # find definitive reward at terminal state

              elif next_s is not None: # if next state is not null if in intermediate state
                if reward(s) == 0: 
                  TDvalues[s] += (10/(9 + N_td[s]))*(0.9*TDvalues[next_s] - TDvalues[s]) # TD update equation for intermediate states
                else: # if reward is nonzero (-1 or 1), break out of simulation after reward update
                  TDvalues[s] += (10/(9 + N_td[s]))*(reward(s) + 0.9*TDvalues[next_s] - TDvalues[s])
                  break

              s = next_s # current state is now next_state

        if autoQL:
          for i in range(1000):
            # copy initial states
            cards_left = copy.copy(ccards)
            user_cards = copy.copy(userCard)
            dealer_cards = copy.copy(dealCard)

            # random state generation
            vals = initGame(cards_left, user_cards, dealer_cards)
            s = make_state(vals[0], vals[1], vals[4], vals[5])
            deal_sum = vals[2]
            deal_a = vals[3]

            while s is not None:
              N_q[s] += 1 # keep track of how many visits to the state

              epsilon = 0.4 # epsilon for epsilon-greedy policy

              a = pick_action(s, epsilon, Qvalues) # pick action given state 
              
              next_s = simulate_one_step_Q(s, a, cards_left, user_cards) # find next state given current state

              if next_s is None: # next state null if final state has been reached

                # simulate dealer's moves from final state to terminal state
                if deal_sum != 21:
                  while deal_sum <= s[0] and deal_sum < 17:
                    next_dealer_card = genCard(cards_left, dealer_cards)

                    deal_sum += getAmt(next_dealer_card[0])
                    deal_a += next_dealer_card[1]

                    while deal_sum > 21 and deal_a > 0:
                      deal_a -= 1
                      deal_sum -= 10
                
                Qvalues[s][a] += (1/(1 + N_q[s]))*(reward_to_go(s, deal_sum) - Qvalues[s][a]) # find definitive reward at terminal state

              elif next_s is not None: # if next state is not null if in intermediate state
                if reward(s) == 0:
                  Qvalues[s][a] += (1/(1 + N_q[s]))*(0.1*max(Qvalues[next_s]) - Qvalues[s][a]) # Q-learning update equation for intermediate states
                else: # if reward is nonzero (-1 or 1), break out of simulation after reward update
                  Qvalues[s][a] += (1/(1 + N_q[s]))*(reward(s) + 0.1*max(Qvalues[next_s]) - Qvalues[s][a])
                  break
              
              s = next_s # current state is now next_state

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            #Clicking the white buttons can start or pause the learning processes
            elif event.type == pygame.MOUSEBUTTONDOWN and MCB.collidepoint(pygame.mouse.get_pos()):
                autoMC = not autoMC
            elif event.type == pygame.MOUSEBUTTONDOWN and TDB.collidepoint(pygame.mouse.get_pos()):
                autoTD = not autoTD
            elif event.type == pygame.MOUSEBUTTONDOWN and QLB.collidepoint(pygame.mouse.get_pos()):
                autoQL = not autoQL
            elif event.type == pygame.MOUSEBUTTONDOWN and (gameover or stand):
                #restarts the game, updating scores
                if userSum == dealSum:
                    pass
                elif userSum <= 21 and len(userCard) == 5:
                    winNum += 1
                elif userSum <= 21 and dealSum < userSum or dealSum > 21:
                    winNum += 1
                else:
                    loseNum += 1
                gameover = False
                stand = False
                userCard = []
                dealCard = []
                ccards = copy.copy(cards)
                userSum, userA, dealSum, dealA, dealFirst, dealAFirst = initGame(ccards, userCard, dealCard)
            elif event.type == pygame.MOUSEBUTTONDOWN and not (gameover or stand) and hitB.collidepoint(pygame.mouse.get_pos()):
                #Give player a card
                card, cA = genCard(ccards, userCard)
                userA += cA
                userSum += getAmt(card)
                while userSum > 21 and userA > 0:
                    userA -= 1
                    userSum -= 10
            elif event.type == pygame.MOUSEBUTTONDOWN and not gameover and standB.collidepoint(pygame.mouse.get_pos()):
                #Dealer plays, user stands
                stand = True
                if dealSum == 21:
                    pass
                else:
                    while dealSum <= userSum and dealSum < 17:
                        card, cA = genCard(ccards, dealCard)
                        dealA += cA
                        dealSum += getAmt(card)
                        while dealSum > 21 and dealA > 0:
                            dealA -= 1
                            dealSum -= 10
        state = make_state(userSum, userA, dealFirst, dealAFirst)
        MCU = font.render('MC-Utility of Current State: %f' % MCvalues[state], 1, black)
        TDU = font.render('TD-Utility of Current State: %f' % TDvalues[state], 1, black)
        QV = font.render('Q values: (Hit) %f (Stand) %f' % tuple(Qvalues[state]) , 1, black)
        winTxt = font.render('Wins: %i' % winNum, 1, white)
        loseTxt = font.render('Losses: %i' % loseNum, 1, white)
        screen.blit(background, (0, 0))
        screen.blit(hitTxt, (39, 448))
        screen.blit(standTxt, (116, 448))
        screen.blit(MCTxt, (193, 448))
        screen.blit(TDTxt, (280, 448))
        screen.blit(QLTxt, (357, 448))
        screen.blit(winTxt, (550, 423))
        screen.blit(loseTxt, (550, 448))
        screen.blit(MCU, (20, 200))
        screen.blit(TDU, (20, 220))
        screen.blit(QV, (20, 240))
        for card in dealCard:
            x = 10 + dealCard.index(card) * 110
            screen.blit(card, (x, 10))
        screen.blit(cBack, (120, 10))
        for card in userCard:
            x = 10 + userCard.index(card) * 110
            screen.blit(card, (x, 295))
        if gameover or stand:
            screen.blit(gameoverTxt, (270, 200))
            screen.blit(dealCard[1], (120, 10))
        pygame.display.update()

if __name__ == '__main__':
    main()

