import random
import logging
import numpy as np
import time
from pygammon import config as cf


class GameState:
    def __init__(self, state=None, empty=False):
        if state is not None:
            self.state = state
        else:
            self.state = np.empty((2, 26), dtype=np.int)  # 2 players, 15 tokens per player
            if not empty:
                # Setup game
                # Last positions are goal and prison in that order
                self.state[0] = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 3, 0, 5, 0, 0, 0, 0, 0, 0, 0]
                self.state[1] = [0, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0]

    def copy(self):
        return GameState(self.state.copy())

    def __getitem__(self, item):
        return self.state[item]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __iter__(self):
        return self.state.__iter__()

    def __eq__(self, other):
        """Overrides the default implementation"""
        return np.array_equal(self.state, other.state)

    def toString(self):
        return str(self[:])

    def getStateRelativeToPlayer(self, relativePlayerID):
        '''
        :param relativePlayerID: Player id
        :return:
        '''
        if relativePlayerID == 0:
            return GameState(self.state.copy())

        rel = GameState(empty=True)
        newPlayerIDs = 1
        rel0 = np.flip(self.state[1][0:24:1])
        rel[0] = np.append(rel0, self.state[1][24:26:1])
        rel1 = np.flip(self.state[0][0:24:1])
        rel[1] = np.append(rel1, self.state[0][24:26:1])
        return rel

    @staticmethod
    def _move(state, tokenIdx, die):
        return

    def moveToken(self, diceRolls):
        '''
        :param diceRolls: Two values between 1 and 6 on a list
        :return:
        '''
        # diceRolls is a list of the two dice rolls
        possibleStates = []
        indices = np.where(self[0] > 0)[0]
        for x in indices:
            for y in indices:
                newState = self.copy()
                player = newState[0]
                opponents = newState[1]

                firstTargetPos = x + diceRolls[0]
                secondTargetPos = y + diceRolls[1]

                if x == cf.GOAL or y == cf.GOAL:
                    continue

                prison = self[0][cf.PRISON]
                # If more than one of the tokens are in "prison"
                if prison > 1:
                    # If it is not both of the tokens, no move possible
                    if not (x == cf.PRISON and y == cf.PRISON):
                        continue
                    else:
                        if opponents[diceRolls[0] - 1] > 1 or opponents[diceRolls[1] - 1] > 1:
                            continue
                        if opponents[diceRolls[0] - 1] == 1:
                            opponents[diceRolls[0] - 1] -= 1
                            opponents[cf.PRISON] += 1
                        if opponents[diceRolls[1] - 1] == 1:
                            opponents[diceRolls[1] - 1] -= 1
                            opponents[cf.PRISON] += 1
                        player[diceRolls[0] - 1] += 1
                        player[cf.PRISON] -= 1
                        player[diceRolls[1] - 1] += 1
                        player[cf.PRISON] -= 1
                        possibleStates.append(newState)

                # If only one of the tokens are in "prison"
                elif prison == 1:
                    # If it is not one of the tokens, no move possible
                    if not (x == cf.PRISON or y == cf.PRISON):
                        continue
                    elif x == y:
                        if opponents[diceRolls[0] - 1] < 2 and opponents[diceRolls[0] - 1 + diceRolls[1]] < 2:
                            if opponents[diceRolls[0] - 1] == 1:
                                opponents[diceRolls[0] - 1] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[diceRolls[0] - 1 + diceRolls[1]] == 1:
                                opponents[diceRolls[0] - 1 + diceRolls[1]] -= 1
                                opponents[cf.PRISON] += 1
                            player[diceRolls[0] - 1 + diceRolls[1]] += 1
                            player[cf.PRISON] -= 1
                            possibleStates.append(newState)
                        newState = self.copy()
                        player = newState[0]
                        opponents = newState[1]
                        if opponents[diceRolls[1] - 1] < 2 and opponents[diceRolls[1] - 1 + diceRolls[0]] < 2:
                            if opponents[diceRolls[1] - 1] == 1:
                                opponents[diceRolls[1] - 1] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[diceRolls[1] - 1 + diceRolls[0]] == 1:
                                opponents[diceRolls[1] - 1 + diceRolls[0]] -= 1
                                opponents[cf.PRISON] += 1
                            player[diceRolls[1] - 1 + diceRolls[0]] += 1
                            player[cf.PRISON] -= 1
                            possibleStates.append(newState)
                    else:
                        if x == cf.PRISON:
                            if secondTargetPos > 23:
                                continue
                            if opponents[diceRolls[0] - 1] > 1 or opponents[secondTargetPos] > 1:
                                continue
                            if opponents[diceRolls[0] - 1] == 1:
                                opponents[diceRolls[0] - 1] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[secondTargetPos] == 1:
                                opponents[secondTargetPos] -= 1
                                opponents[cf.PRISON] += 1

                            player[diceRolls[0] - 1] += 1
                            player[cf.PRISON] -= 1
                            player[secondTargetPos] += 1
                            player[y] -= 1
                            possibleStates.append(newState)
                        else:
                            if firstTargetPos > 23:
                                continue
                            if opponents[firstTargetPos] > 1 or opponents[diceRolls[1] - 1] > 1:
                                continue
                            if opponents[firstTargetPos] == 1:
                                opponents[firstTargetPos] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[diceRolls[1] - 1] == 1:
                                opponents[diceRolls[1] - 1] -= 1
                                opponents[cf.PRISON] += 1
                            player[firstTargetPos] += 1
                            player[x] -= 1
                            player[diceRolls[1] - 1] += 1
                            player[cf.PRISON] -= 1
                            possibleStates.append(newState)
                else:
                    if x == y:
                        if firstTargetPos < 24 and opponents[firstTargetPos] < 2 \
                                and firstTargetPos + diceRolls[1] < 24 and opponents[firstTargetPos + diceRolls[1]] < 2:
                            if opponents[firstTargetPos] == 1:
                                opponents[firstTargetPos] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[firstTargetPos + diceRolls[1]] == 1:
                                opponents[firstTargetPos + diceRolls[1]] -= 1
                                opponents[cf.PRISON] += 1
                            player[firstTargetPos + diceRolls[1]] += 1
                            player[x] -= 1
                            possibleStates.append(newState)
                        newState = self.copy()
                        player = newState[0]
                        opponents = newState[1]
                        if secondTargetPos < 24 and opponents[secondTargetPos] < 2 \
                                and secondTargetPos + diceRolls[0] < 24 and opponents[
                            secondTargetPos + diceRolls[0]] < 2:
                            if opponents[secondTargetPos] == 1:
                                opponents[secondTargetPos] -= 1
                                opponents[cf.PRISON] += 1
                            if opponents[secondTargetPos + diceRolls[0]] == 1:
                                opponents[secondTargetPos + diceRolls[0]] -= 1
                                opponents[cf.PRISON] += 1
                            player[secondTargetPos + diceRolls[0]] += 1
                            player[x] -= 1
                            possibleStates.append(newState)
                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]
                    if firstTargetPos > 23 or opponents[firstTargetPos] > 1 or secondTargetPos > 23 or opponents[
                        secondTargetPos] > 1:
                        continue
                    if x == y and player[x] < 2:
                        continue
                    # Check for opponent occupied by spaces
                    if opponents[firstTargetPos] == 1:
                        opponents[firstTargetPos] -= 1
                        opponents[cf.PRISON] += 1
                    if opponents[secondTargetPos] == 1:
                        opponents[secondTargetPos] -= 1
                        opponents[cf.PRISON] += 1
                    player[firstTargetPos] += 1
                    player[x] -= 1
                    player[secondTargetPos] += 1
                    player[y] -= 1
                    possibleStates.append(newState)

        return np.asarray(possibleStates)

    def moveTokenHome(self, diceRolls):
        '''
        :param diceRolls: Two values between 1 and 6 on a list
        :return:
        '''
        # diceRolls is a list of the two dice rolls
        possibleStates = []
        indices = np.where(self[0] > 0)[0]
        minPos = np.min(indices)
        for x in indices:
            for y in indices:
                firstTargetPos = x + diceRolls[0]
                secondTargetPos = y + diceRolls[1]
                if x == cf.GOAL or y == cf.GOAL:
                    continue
                newState = self.copy()
                player = newState[0]
                opponents = newState[1]

                if x == y:
                    # MOVE THEN HOME x2

                    if (firstTargetPos < 24 and opponents[firstTargetPos] < 2) \
                            and ((12 - (firstTargetPos - 12)) == diceRolls[1]
                                 or (firstTargetPos == minPos and firstTargetPos +
                                     diceRolls[1] > 23)):
                        if opponents[firstTargetPos] == 1:
                            opponents[firstTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        player[cf.GOAL] += 1
                        player[x] -= 1
                        possibleStates.append(newState)

                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]
                    if (secondTargetPos < 24 and opponents[secondTargetPos] < 2) \
                            and ((12 - (secondTargetPos - 12)) == diceRolls[0]
                                 or (firstTargetPos + diceRolls[0] == minPos and firstTargetPos +
                                     diceRolls[0] > 23)):
                        if opponents[secondTargetPos] == 1:
                            opponents[secondTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        player[cf.GOAL] += 1
                        player[y] -= 1
                        possibleStates.append(newState)

                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]

                    # MOVE TWICE x2
                    if firstTargetPos < 24 and opponents[firstTargetPos] < 2 \
                            and firstTargetPos + diceRolls[1] < 24 and opponents[firstTargetPos + diceRolls[1]] < 2:
                        if opponents[firstTargetPos] == 1:
                            opponents[firstTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        if opponents[firstTargetPos + diceRolls[1]] == 1:
                            opponents[firstTargetPos + diceRolls[1]] -= 1
                            opponents[cf.PRISON] += 1
                        player[firstTargetPos + diceRolls[1]] += 1
                        player[x] -= 1
                        possibleStates.append(newState)
                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]
                    if secondTargetPos < 24 and opponents[secondTargetPos] < 2 \
                            and secondTargetPos + diceRolls[0] < 24 and opponents[secondTargetPos + diceRolls[0]] < 2:
                        if opponents[secondTargetPos] == 1:
                            opponents[secondTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        if opponents[secondTargetPos + diceRolls[0]] == 1:
                            opponents[secondTargetPos + diceRolls[0]] -= 1
                            opponents[cf.PRISON] += 1
                        player[secondTargetPos + diceRolls[0]] += 1
                        player[x] -= 1
                        possibleStates.append(newState)

                newState = self.copy()
                player = newState[0]
                opponents = newState[1]

                if x == y and player[x] < 2:  # If there is less than 2 players
                    continue

                if ((12 - (x - 12)) == diceRolls[0]) or (x == minPos and x + diceRolls[0] > 23):
                    player[x] -= 1
                    player[cf.GOAL] += 1
                    if ((12 - (y - 12)) == diceRolls[1]) or (y == minPos and y + diceRolls[1] > 23):
                        player[y] -= 1
                        player[cf.GOAL] += 1
                        possibleStates.append(newState)

                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]

                    player[x] -= 1
                    player[cf.GOAL] += 1
                    if secondTargetPos < 24 and opponents[secondTargetPos] < 2:
                        if opponents[secondTargetPos] == 1:
                            opponents[secondTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        player[secondTargetPos] += 1
                        player[y] -= 1
                        possibleStates.append(newState)

                newState = self.copy()
                player = newState[0]
                opponents = newState[1]

                if firstTargetPos < 24 and opponents[firstTargetPos] < 2:
                    if opponents[firstTargetPos] == 1:
                        opponents[firstTargetPos] -= 1
                        opponents[cf.PRISON] += 1
                    player[firstTargetPos] += 1
                    player[x] -= 1
                    if ((12 - (y - 12)) == diceRolls[1]) or (y == minPos and y + diceRolls[1] > 23):
                        player[y] -= 1
                        player[cf.GOAL] += 1
                        possibleStates.append(newState)

                    newState = self.copy()
                    player = newState[0]
                    opponents = newState[1]
                    if opponents[firstTargetPos] == 1:
                        opponents[firstTargetPos] -= 1
                        opponents[cf.PRISON] += 1
                    player[firstTargetPos] += 1
                    player[x] -= 1

                    if secondTargetPos < 24 and opponents[secondTargetPos] < 2:
                        if opponents[secondTargetPos] == 1:
                            opponents[secondTargetPos] -= 1
                            opponents[cf.PRISON] += 1
                        player[secondTargetPos] += 1
                        player[y] -= 1
                        possibleStates.append(newState)
        return np.asarray(possibleStates)

    def moveOneToken(self, diceRolls):
        possibleStates = []
        indices = np.where(self[0] > 0)[0]
        for x in indices:
            newState = self.copy()
            player = newState[0]
            opponents = newState[1]
            if x == cf.GOAL:
                continue
            if player[cf.PRISON] > 0 and x == cf.PRISON:
                if opponents[diceRolls[0] - 1] > 1:
                    continue
                if opponents[diceRolls[0] - 1] == 1:
                    opponents[diceRolls[0] - 1] -= 1
                    opponents[cf.PRISON] += 1
                player[diceRolls[0] - 1] += 1
                player[cf.PRISON] -= 1
                possibleStates.append(newState)
            elif player[cf.PRISON] == 0:
                targetPos = x + diceRolls[0]
                if targetPos < 24 and opponents[targetPos] < 2:
                    if opponents[targetPos] == 1:
                        opponents[targetPos] -= 1
                        opponents[cf.PRISON] += 1
                    player[targetPos] += 1
                    player[x] -= 1
                    possibleStates.append(newState)

        for y in indices:
            newState = self.copy()
            player = newState[0]
            opponents = newState[1]
            if y == cf.GOAL:
                continue
            if player[cf.PRISON] > 0 and y == cf.PRISON:
                if opponents[diceRolls[1] - 1] > 1:
                    continue
                if opponents[diceRolls[1] - 1] == 1:
                    opponents[diceRolls[1] - 1] -= 1
                    opponents[cf.PRISON] += 1
                player[diceRolls[1] - 1] += 1
                player[cf.PRISON] -= 1
                possibleStates.append(newState)
            elif player[cf.PRISON] == 0:
                targetPos = y + diceRolls[1]
                if targetPos < 24 and opponents[targetPos] < 2:
                    if opponents[targetPos] == 1:
                        opponents[targetPos] -= 1
                        opponents[cf.PRISON] += 1
                    player[targetPos] += 1
                    player[y] -= 1
                    possibleStates.append(newState)

        return np.asarray(possibleStates)

    def moveOneTokenHome(self, diceRolls):
        '''
        :param diceRolls: Two values between 1 and 6 on a list
        :return:
        '''
        possibleStates = []
        indices = np.where(self[0] > 0)[0]
        minPos = np.min(indices)
        for x in indices:
            if x == cf.GOAL:
                continue
            newState = self.copy()
            player = newState[0]
            opponents = newState[1]
            targetPos = x + diceRolls[0]

            if ((12 - (x - 12)) == diceRolls[0]) or (x == minPos and x + diceRolls[0] > 23):
                player[x] -= 1
                player[cf.GOAL] += 1
                possibleStates.append(newState)

            newState = self.copy()
            player = newState[0]
            opponents = newState[1]

            if targetPos < 24 and opponents[targetPos] < 2:
                if opponents[targetPos] == 1:
                    opponents[targetPos] -= 1
                    opponents[cf.PRISON] += 1
                player[targetPos] += 1
                player[x] -= 1
                possibleStates.append(newState)

        for y in indices:
            if y == cf.GOAL:
                continue
            newState = self.copy()
            player = newState[0]
            opponents = newState[1]

            targetPos = y + diceRolls[1]

            if ((12 - (y - 12)) == diceRolls[1]) or (y == minPos and y + diceRolls[1] > 23):
                player[y] -= 1
                player[cf.GOAL] += 1
                possibleStates.append(newState)

            newState = self.copy()
            player = newState[0]
            opponents = newState[1]

            if targetPos < 24 and opponents[targetPos] < 2:
                if opponents[targetPos] == 1:
                    opponents[targetPos] -= 1
                    opponents[cf.PRISON] += 1
                player[targetPos] += 1
                player[y] -= 1
                possibleStates.append(newState)
        return np.asarray(possibleStates)

    @staticmethod
    def getWinner(state):
        '''
        :return: Winner of the game
        '''
        for player_id in range(2):
            if state[player_id][cf.GOAL] == 15:
                return player_id
        return -1


class Game:
    def __init__(self, players, state=None):
        assert len(players) == 2, "There must be 2 players in the game"
        self.players = players
        self.currentPlayerId = -1
        self.state = GameState() if state is None else state
        self.stepCount = 0

    @staticmethod
    def trimStates(possibleStates):
        # TODO Optimize the code if possible
        # nowTime = time.time()
        if len(possibleStates) == 0:
            return possibleStates
        states = []
        for x in range(len(possibleStates)):
            if not possibleStates[x] in states:
                states.append(possibleStates[x])
        # print("TimeList:", (time.time() - nowTime))
        # print("DIFF:", len(possibleStates)-len(states))
        return np.asarray(states)

    @staticmethod
    def getRelativeStates(currentState, diceRolls):
        if not sum(currentState[0][0:26:1]) == 15:
            print(sum(currentState[0][0:26:1]))
        if sum(currentState[0][18:25:1]) == 15:
            relativeNextStates = currentState.moveTokenHome(diceRolls)

            if not len(relativeNextStates):
                relativeNextStates = currentState.moveOneTokenHome(diceRolls)
        else:
            relativeNextStates = currentState.moveToken(diceRolls)

            if not len(relativeNextStates):
                relativeNextStates = currentState.moveOneToken(diceRolls)
        return relativeNextStates

    def step(self, debug=False):
        state = self.state
        self.currentPlayerId = (self.currentPlayerId + 1) % 2
        player = self.players[self.currentPlayerId]
        diceRolls = [random.randint(1, 6), random.randint(1, 6)]
        if debug:
            playerName = "red" if self.currentPlayerId == 1 else "blue"
            print("Player: ", playerName)
            print("Dice Rolls", diceRolls)
        relativeState = state.getStateRelativeToPlayer(self.currentPlayerId)
        # print(player.name, relativeState.state)

        relativeNextStates = Game.getRelativeStates(relativeState, diceRolls)
        if relativeNextStates.size > 0:
            nextStateID = player.play(relativeState, diceRolls, relativeNextStates)
            if not nextStateID > - 1:
                return
            if nextStateID > relativeNextStates.size - 1:
                logging.warning("Player chose invalid move. Choosing first valid move.")
                nextStateID = relativeNextStates[0]
            self.state = relativeNextStates[nextStateID].getStateRelativeToPlayer((-self.currentPlayerId) % 2)
            # print("Player 1",  " State: ", self.state[0])
            # print("Player 2", " State: ", self.state[1])

    def playFullGame(self, get_step=False):
        while self.state.getWinner(self.state) == -1:
            # print("Player 1", " State: ", self.state[0])
            # print("Player 2", " State: ", self.state[1])
            self.step()
            self.stepCount += 1
        #if self.players[0].name == "monte-carlo" or self.players[1].name == "monte-carlo":
            #print("Game moves", self.stepCount)
        if get_step:
            return self.state.getWinner(self.state), self.stepCount
        #if self.players[0].name == "TD-gammon":
        #    self.players[0].reset_step()
        #if self.players[1].name == "TD-gammon":
        #    self.players[1].reset_step()

        return self.state.getWinner(self.state)
