#!/usr/bin/env python

#########
# 2014 Copyright (C) Simon Mouradian
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#########

from Tkinter import *

import string
import random
import ai_controller

ai = ai_controller.PID(I=0.5)

single_player = False

sounds_enabled = False
try:
    from pygame import mixer
    sounds_enabled = True
except:
    pass

WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 14
PAD_WIDTH = 14
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
LEFT = False
RIGHT = True

LINE_COLOUR='white'
BALL_COLOUR='white'
PADDLE1_COLOUR='blue'
PADDLE2_COLOUR='red'
paddle_acc = 8

def ball_bbox(ball_pos):
    return ball_pos[0]-BALL_RADIUS, ball_pos[1]-BALL_RADIUS, ball_pos[0]+BALL_RADIUS, ball_pos[1]+BALL_RADIUS

def reset_ball(direction):
    global ball, ball_pos, ball_vel
    ball_pos = [WIDTH/2, HEIGHT/2]
    canvas.coords(ball, ball_bbox(ball_pos))
    if direction==RIGHT:
        ball_vel = [random.randrange(2,4),-random.randrange(1,2)]
    else:
        ball_vel = [-random.randrange(2,4),-random.randrange(1,2)]

def draw_movable_items():
    global ball, ball_pos, paddle1, paddle1_pos, paddle2, paddle2_pos
    ball_pos = [WIDTH/2, HEIGHT/2]
    paddle1_pos = HEIGHT/2
    paddle2_pos = HEIGHT/2
    ball = canvas.create_oval(ball_bbox(ball_pos),fill=BALL_COLOUR)
    paddle1 = canvas.create_rectangle(0, paddle1_pos+HALF_PAD_HEIGHT, \
                                          PAD_WIDTH, paddle1_pos-HALF_PAD_HEIGHT, \
                                          fill=PADDLE1_COLOUR)
    paddle2 = canvas.create_rectangle(WIDTH-PAD_WIDTH, paddle2_pos+HALF_PAD_HEIGHT, \
                                          WIDTH, paddle2_pos-HALF_PAD_HEIGHT,\
                                          fill=PADDLE2_COLOUR)

def toggle_computer():
    global single_player
    if single_player_int.get() == 0:
        single_player = False
    else:
        single_player = True

def new_game():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel
    global score1, score2, score1_label, score2_label
    if sounds_enabled:
        new_game_sound.play()
    paddle1_pos = HEIGHT/2
    paddle2_pos = HEIGHT/2
    paddle1_vel = 0
    paddle2_vel = 0
    score1 = 0
    canvas.itemconfigure(score1_label,text=str(score1))
    score2 = 0
    canvas.itemconfigure(score2_label,text=str(score2))
    reset_ball(RIGHT)
    
def dynamics():
    global score1,score2,paddle1_pos,paddle2_pos,ball_pos, ball_vel

    if single_player == True:
        ## AI Dynamics here
        global paddle1_vel
        paddle_height = 0.5 * sum(canvas.coords(paddle1)[1::2])
        ball_height = 0.5 * sum(canvas.coords(ball)[1::2])

        paddle1_vel = 0.01 * ai.update(paddle_height - ball_height)

    canvas.move(paddle1,0,paddle1_vel)
    canvas.move(paddle2,0,paddle2_vel)
    canvas.move(ball,ball_vel[0],ball_vel[1])

    if canvas.coords(paddle1)[1]<=0:
        canvas.coords(paddle1,0,0,PAD_WIDTH,PAD_HEIGHT)
    elif canvas.coords(paddle1)[3]>=HEIGHT:
        canvas.coords(paddle1,0,HEIGHT-PAD_HEIGHT,PAD_WIDTH,HEIGHT)

    if canvas.coords(paddle2)[1]<=0:
        canvas.coords(paddle2,WIDTH-PAD_WIDTH, 0, WIDTH, PAD_HEIGHT)
    elif canvas.coords(paddle2)[3]>=HEIGHT:
        canvas.coords(paddle2,WIDTH-PAD_WIDTH, HEIGHT-PAD_HEIGHT, WIDTH, HEIGHT)

    if canvas.coords(ball)[1] <= 0:
        ball_vel[1] = - ball_vel[1]
    if canvas.coords(ball)[3] >= HEIGHT:
        ball_vel[1] = - ball_vel[1]

    if canvas.coords(ball)[2] >= WIDTH-PAD_WIDTH:
        ball_height = 0.5 * sum(canvas.coords(ball)[1::2])
        paddle_height = 0.5 * sum(canvas.coords(paddle2)[1::2])
        if abs(ball_height - paddle_height) < HALF_PAD_HEIGHT:
            if sounds_enabled:
                paddle_bounce.play()
            ball_vel[0] = - (ball_vel[0]* 1.08)
            ball_vel[1] = 7 * (ball_height - paddle_height) / HALF_PAD_HEIGHT
        else:
            score1 += 1
            canvas.itemconfigure(score1_label,text=str(score1))
            reset_ball(LEFT)

    if canvas.coords(ball)[0] <= PAD_WIDTH:
        ball_height = 0.5 * sum(canvas.coords(ball)[1::2])
        paddle_height = 0.5 * sum(canvas.coords(paddle1)[1::2])
        #if ball_height > canvas.coords(paddle1)[1] and ball_height < canvas.coords(paddle1)[3]:
        if abs(ball_height - paddle_height) < HALF_PAD_HEIGHT:
            if sounds_enabled:
                paddle_bounce.play()
            ball_vel[0] = - (ball_vel[0] * 1.08)
            ball_vel[1] = 7 * (ball_height - paddle_height) / HALF_PAD_HEIGHT
        else:
            score2 += 1
            canvas.itemconfigure(score2_label,text=str(score2))
            reset_ball(RIGHT)

    canvas.after(10,dynamics)

def upPressed(event):
    global paddle2_vel
    paddle2_vel = -paddle_acc

def upReleased(event):
    global paddle2_vel
    paddle2_vel = 0

def downPressed(event):
    global paddle2_vel
    paddle2_vel = paddle_acc

def downReleased(event):
    global paddle2_vel
    paddle2_vel = 0

def KeyPressed(event):
    global paddle1_vel, paddle2_vel
    if event.char == 'w':
        paddle1_vel = -paddle_acc
    elif event.char == 's':
        paddle1_vel = paddle_acc
    elif event.char == 'o':
        paddle2_vel = -paddle_acc
    elif event.char == 'l':
        paddle2_vel = paddle_acc

def KeyReleased(event):
    global paddle1_vel, paddle2_vel
    if event.char == 'w':
        paddle1_vel = 0
    elif event.char == 's':
        paddle1_vel = 0
    elif event.char == 'o':
        paddle2_vel = 0
    elif event.char == 'l':
        paddle2_vel = 0

def draw_scores():
    global score1_label, score2_label
    score1_label = canvas.create_text((WIDTH/2)-40, 40, text='0',\
                                          font=('TkDefaultFont',40),\
                                          fill=LINE_COLOUR)
    score2_label = canvas.create_text((WIDTH/2)+40, 40, text='0',\
                                          font=('TkDefaultFont',40),\
                                          fill=LINE_COLOUR)

def load_sounds():
    global paddle_bounce, new_game_sound
    mixer.init(44100)
    paddle_bounce = mixer.Sound('sounds/paddle_bounce.wav')
    new_game_sound = mixer.Sound('sounds/new_game.wav')

# Create master frame and drawing canvas.
frame = Tk()
frame.title('Pong')
canvas = Canvas(frame, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()

# Draw the battle lines!
canvas.create_line(WIDTH/2, 0, WIDTH/2, HEIGHT, fill=LINE_COLOUR)
canvas.create_line(PAD_WIDTH,0, PAD_WIDTH,HEIGHT, fill=LINE_COLOUR)
canvas.create_line(WIDTH-PAD_WIDTH,0, WIDTH-PAD_WIDTH,HEIGHT, fill=LINE_COLOUR)

# Register key event handlers
frame.bind('<Up>', upPressed)
frame.bind('<KeyRelease-Up>', upReleased)
frame.bind('<Down>', downPressed)
frame.bind('<KeyRelease-Down>', downReleased)
frame.bind('<Key>', KeyPressed)
frame.bind('<KeyRelease>', KeyReleased)

# Draw the ball and paddles
draw_movable_items()

resetButton = Button(frame, text ="Reset Scores", command = new_game)
resetButton.pack(side='left')

single_player_int = IntVar()
toggleComputer = Checkbutton(frame,
                             text="Toggle Computer",
                             variable = single_player_int,
                             command = toggle_computer)
toggleComputer.pack(side='left')

# toggleComputerButton = Button(frame, text="Toggle Computer", command = toggle_computer)
# toggleComputerButton.pack(side='left')



if sounds_enabled:
    load_sounds()
draw_scores()
new_game()

dynamics()
frame.mainloop()
