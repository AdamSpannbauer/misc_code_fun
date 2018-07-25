# Create/animate fractal trees at various angles for branch splits

library(gganimate)
library(ggplot2)
library(uuid)
options(stringsAsFactors = FALSE)

# create line segment from (0, 0) to (0, len) to be trunk of fractal tree
create_trunk = function(len = 1) {
  end_point = c(0, len)
  trunk_df = data.frame(x=c(0, 0),
                        y=end_point,
                        id=uuid::UUIDgenerate())
  
  return(list(df=trunk_df, end_point=end_point))
}

# creates end point of line segment to satisfy length and
# angle inputs from given start coord
gen_end_point = function(xy, len = 5, theta = 45) {
  dy = sin(theta) * len
  dx = cos(theta) * len
  
  newx = xy[1] + dx
  newy = xy[2] + dy
  return(c(newx, newy))
}

# create a single branch of fractal tree
# returns branch endpoint coords and a plotly line shape to represent branch
branch = function(xy, angle_in, delta_angle, len) {
  end_point = gen_end_point(xy, len = len, theta = angle_in + delta_angle)
  branch_df = as.data.frame(rbind(xy, end_point))
  rownames(branch_df) = NULL
  names(branch_df) = c('x', 'y')
  branch_df$id = uuid::UUIDgenerate()
  
  return(list(df=branch_df, end_point=end_point))
}

# helper function to aggregate branch objects into single branch object
collect_branches = function(branch1, branch2) {
  return(list(df=rbind(branch1$df, branch2$df)))
}

# recursively create fractal tree branches
create_branches = function(xy,
                           angle_in = pi / 2,
                           delta_angle = pi / 8,
                           len = 1,
                           min_len = 0.01,
                           len_decay = 0.2) {
  if (len < min_len) {
    return(NULL)
  } else {
    branch_left = branch(xy, angle_in, delta_angle, len)
    subranches_left = create_branches(branch_left$end_point,
                                      angle_in = angle_in + delta_angle,
                                      delta_angle = delta_angle,
                                      len = len * len_decay,
                                      min_len = min_len,
                                      len_decay = len_decay)
    branches_left = collect_branches(branch_left, subranches_left)
    
    branch_right = branch(xy, angle_in, -delta_angle, len)
    subranches_right = create_branches(branch_right$end_point,
                                       angle_in = angle_in - delta_angle,
                                       delta_angle = delta_angle,
                                       len = len * len_decay,
                                       min_len = min_len,
                                       len_decay = len_decay)
    branches_right = collect_branches(branch_right, subranches_right)
    
    return(collect_branches(branches_left, branches_right))
  }
}

# create full fractal tree
create_fractal_tree_df = function(trunk_len=10,
                                  delta_angle = pi / 8,
                                  len_decay=0.7,
                                  min_len=0.25) {
  trunk = create_trunk(trunk_len)
  branches = create_branches(trunk$end_point,
                             delta_angle = delta_angle,
                             len = trunk_len * len_decay,
                             min_len = min_len,
                             len_decay = len_decay)
  
  tree = collect_branches(trunk, branches)$df
  
  return(tree)
}

# create a series of trees from a sequence of angles for branch splits
create_fractal_tree_seq = function(trunk_len=10,
                                   angle_seq=seq(0, pi, pi/16),
                                   len_decay=0.7,
                                   min_len=0.25) {
  
  tree_list = lapply(seq_along(angle_seq), function(i) {
    tree_i = create_fractal_tree_df(trunk_len, 
                                    angle_seq[i],
                                    len_decay,
                                    min_len)
    tree_i$frame = i
    tree_i$angle = angle_seq[i]
    
    return(tree_i)
  })
  
  return(do.call(rbind, tree_list))
}

# create/animate a series of trees using gganimate
animate_fractal_tree = function(trunk_len=10,
                                angle_seq=seq(0, pi, pi/16),
                                len_decay=0.7,
                                min_len=0.25,
                                filename=NULL) {
  trees = create_fractal_tree_seq(trunk_len,
                                  angle_seq,
                                  len_decay,
                                  min_len)
  
  ggplot(trees, aes(x, y, group=id)) +
    geom_line() +
    geom_point(size=.2, aes(color=angle)) +
    scale_color_gradientn(colours = rainbow(5)) +
    guides(color=FALSE) +
    theme_void() +
    transition_manual(frame)
}

# example usage
animate_fractal_tree(trunk_len=10,
                     angle_seq=seq(0, 2 * pi - pi / 32, pi/32),
                     len_decay=0.7,
                     min_len=.25)
