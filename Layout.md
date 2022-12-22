```
Game
~ Main Object

    step(direction) -> None
    ~ Moves the ballon in direction [a, b, c] by SCREEN_WIDTH//BALLOON_WIDTH
        - a: Left
        - b: None
        - c: Right

    get_state() -> [a, b, c, d, e, f]
    ~ Returns the game_state in 6 variables:
        - a: balloon_x - next_bubble_x
        - b: balloon_y - next_bubble_y
        - c: balloon_x - next_spike_gap_x
        - d: balloon_y - next_spike_gap_y
        - e: balloon_x - prevoius_spike_gap_x
        - f: balloon_y - prevoius_spike_gap_y

    render() -> None
    ~ Renders the current game_state

```

```
Running Sequence:
    game = Game (__init__)
    for genome in genomes:
        game.reset()                //
        while not DEAD:             //
            game.get_state()        //
            (Calculate next move)   //  eval_genome function
            game.step()             //
            game.render_window()    //
        fitness = game.score        //

```
