"""Showcase of flying arrows that can stick to objects in a somewhat 
realistic looking way.
"""
import sys

import pygame
from pygame.locals import *
from pygame.color import *
    
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

def create_arrow():
    vs = [(-30,0), (0,3), (10,0), (0,-3)]
    mass = 1
    moment = pymunk.moment_for_poly(mass, vs)
    arrow_body = pymunk.Body(mass, moment)

    arrow_shape = pymunk.Poly(arrow_body, vs)
    arrow_shape.friction = .5
    arrow_shape.collision_type = 1
    return arrow_body, arrow_shape
    
def stick_arrow_to_target(space, arrow_body, target_body, position, flying_arrows):
    pivot_joint = pymunk.PivotJoint(arrow_body, target_body, position)
    phase = target_body.angle - arrow_body.angle 
    gear_joint = pymunk.GearJoint(arrow_body, target_body, phase, 1)
    space.add(pivot_joint)
    space.add(gear_joint)
    try:
        flying_arrows.remove(arrow_body)
    except:
        pass

def post_solve_arrow_hit(arbiter, space, data):
    if arbiter.total_impulse.length > 300:
        a,b = arbiter.shapes
        position = arbiter.contact_point_set.points[0].point_a
        b.collision_type = 0
        b.group = 1
        other_body = a.body
        arrow_body = b.body
        space.add_post_step_callback(
            stick_arrow_to_target, arrow_body, other_body, position, data["flying_arrows"])
    
width, height = 690,600
def main():
    ### PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width,height)) 
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)
    
    ### Physics stuff
    space = pymunk.Space()   
    space.gravity = 0,-1000
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # walls - the left-top-right walls
    static= [pymunk.Segment(space.static_body, (50, 50), (50, 550), 5)
                ,pymunk.Segment(space.static_body, (50, 550), (650, 550), 5)
                ,pymunk.Segment(space.static_body, (650, 550), (650, 50), 5)
                ,pymunk.Segment(space.static_body, (50, 50), (650, 50), 5)
                ]  
    
    b2 = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    static.append(pymunk.Circle(b2, 30))
    b2.position = 300,400
    
    for s in static:
        s.friction = 1.
        s.group = 1
    space.add(static)
    
    # "Cannon" that can fire arrows
    cannon_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    cannon_shape = pymunk.Circle(cannon_body, 25)
    cannon_shape.sensor = True
    cannon_shape.color = (255,50,50)
    cannon_body.position = 100,100
    space.add(cannon_shape)
    
    arrow_body,arrow_shape = create_arrow()
    space.add(arrow_shape)

    flying_arrows = []    
    handler = space.add_collision_handler(0, 1)
    handler.data["flying_arrows"] = flying_arrows
    handler.post_solve=post_solve_arrow_hit

    
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or \
                event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):  
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                start_time = pygame.time.get_ticks()
            elif event.type == KEYDOWN and event.key == K_p:
                pygame.image.save(screen, "arrows.png")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                end_time = pygame.time.get_ticks()
                
                diff = end_time - start_time
                power = max(min(diff, 1000), 10) * 1.5
                impulse = power * Vec2d(1,0)
                impulse.rotate(arrow_body.angle)
                
                arrow_body.apply_impulse_at_world_point(impulse, arrow_body.position)
                
                space.add(arrow_body)
                flying_arrows.append(arrow_body)
                
                arrow_body, arrow_shape = create_arrow()
                space.add(arrow_shape)
            
        keys = pygame.key.get_pressed()
        
        speed = 2.5
        if (keys[K_UP]):
            cannon_body.position += Vec2d(0,1) * speed
        if (keys[K_DOWN]):
            cannon_body.position += Vec2d(0,-1) * speed
        if (keys[K_LEFT]):
            cannon_body.position += Vec2d(-1,0) * speed
        if (keys[K_RIGHT]):
            cannon_body.position += Vec2d(1,0) * speed
            
        mouse_position = pymunk.pygame_util.from_pygame( Vec2d(pygame.mouse.get_pos()), screen )
        cannon_body.angle = (mouse_position - cannon_body.position).angle
        # move the unfired arrow together with the cannon
        arrow_body.position = cannon_body.position + Vec2d(cannon_shape.radius + 40, 0).rotated(cannon_body.angle)
        arrow_body.angle = cannon_body.angle
        
        
        for flying_arrow in flying_arrows:
            drag_constant = 0.0002
            
            pointing_direction = Vec2d(1,0).rotated(flying_arrow.angle)
            flight_direction = Vec2d(flying_arrow.velocity)
            flight_speed = flight_direction.normalize_return_length()
            dot = flight_direction.dot(pointing_direction)
            # (1-abs(dot)) can be replaced with (1-dot) to make arrows turn 
            # around even when fired straight up. Might not be as accurate, but 
            # maybe look better.
            drag_force_magnitude = (1-abs(dot)) * flight_speed **2 * drag_constant * flying_arrow.mass
            arrow_tail_position = Vec2d(-50, 0).rotated(flying_arrow.angle)
            flying_arrow.apply_impulse_at_world_point(drag_force_magnitude * -flight_direction, arrow_tail_position)
            
            flying_arrow.angular_velocity *= 0.5
            
        ### Clear screen
        screen.fill(pygame.color.THECOLORS["black"])
        
        ### Draw stuff
        space.debug_draw(draw_options)
        #draw(screen, space)
        
        # Power meter
        if pygame.mouse.get_pressed()[0]:
            current_time = pygame.time.get_ticks()
            diff = current_time - start_time
            power = max(min(diff, 1000), 10)
            h = power / 2
            pygame.draw.line(screen, pygame.color.THECOLORS["red"], (30,550), (30,550-h), 10)
                
        # Info and flip screen
        screen.blit(font.render("fps: " + str(clock.get_fps()), 1, THECOLORS["white"]), (0,0))
        screen.blit(font.render("Aim with mouse, hold LMB to powerup, release to fire", 1, THECOLORS["darkgrey"]), (5,height - 35))
        screen.blit(font.render("Press ESC or Q to quit", 1, THECOLORS["darkgrey"]), (5,height - 20))
        
        pygame.display.flip()
        
        ### Update physics
        fps = 60
        dt = 1./fps
        space.step(dt)
        
        clock.tick(fps)

if __name__ == '__main__':
    main()