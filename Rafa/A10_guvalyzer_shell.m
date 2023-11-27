function A10_guvalyzer_shell

%choose experiment:
exp_index=0;  %pilot work red/gre 
exp_index=1;  %2nd pilot. red/blu/gre
%set up:
init=A000_get_config(exp_index);
%process:
if 1, A20_get_areas(init); end
if 1, A25_map_areas(init); end
if 0, A30_link_areas(init); end
if 0, A40_get_vesicle_lifes(init); end
    

