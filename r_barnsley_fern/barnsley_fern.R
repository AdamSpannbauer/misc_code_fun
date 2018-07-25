# Barnsley fern in R
# reference: https://en.wikipedia.org/wiki/Barnsley_fern

library(plotly)

# FUNCTIONS FOR GENERATING BARNSLEY FERN POINTS ################################
transform_1 = function(x, y) {
  x = 0
  y = 0.16 * y
  return(c(x, y))
}

transform_2 = function(x, y) {
  x =  0.85 * x + 0.04 * y
  y = -0.04 * x + 0.85 * y + 1.6
  return(c(x, y))
}

transform_3 = function(x, y) {
  x = 0.20 * x + -0.26 * y
  y = 0.23 * x +  0.22 * y + 1.6
  return(c(x, y))
}

transform_4 = function(x, y) {
  x = -0.15 * x + 0.28 * y
  y =  0.26 * x + 0.24 * y + 0.44
  return(c(x, y))
}

transforms = list(transform_1, transform_2, transform_3, transform_4)
get_next_fern_point = function(x, y) {
  i = sample(1:4, 1, prob = c(0.01, 0.85, 0.07, 0.07))
  trans = transforms[[i]]
  return(trans(x, y))
}

get_fern_points = function(x, y, n = 100) {
  coords = matrix(NA, nrow = n, ncol = 2)
  colnames(coords) = c('x', 'y')
  for (i in 1:n) {
    trans_i = get_next_fern_point(x, y)
    coords[i, ] = trans_i
    x = trans_i[1]
    y = trans_i[2]
  }
  
  return(coords)
}

# FUNCTION FOR DRAWING STATIC FERN WITH BASE PLOT ##############################
draw_barnsley_fern = function(n_points = 1e5, point_color = 'darkgreen') {
  fern_points = get_fern_points(0, 0, n = n_points)
  
  plot(
    fern_points,
    col = point_color,
    pch = 20,
    cex = 0.01,
    xlim = c(-2.1820, 2.6558),
    ylim = c(0, 9.9983),
    xlab = '',
    ylab = '',
    axes = FALSE
  )
}

# FUNCTION FOR CREATING ANIMATION DATA #########################################
create_grow_df = function(fern_points, n_frames = 40) {
  fern_points = as.data.frame(fern_points)
  fern_points$Frame = round(seq(1, n_frames, length.out = nrow(fern_points)))
  frame_0 = data.frame(x = 0, y = 0, Frame = 0)
  fern_points = rbind(frame_0, fern_points)
  
  frames = unique(fern_points$Frame)
  frame_df_list = vector('list', max(frames) + 1)
  for (frame in frames) {
    df_frame = fern_points[fern_points$Frame <= frame, ]
    df_frame$Frame = frame
    frame_df_list[[frame + 1]] = df_frame
  }
  
  grow_fern_df = do.call('rbind', frame_df_list)
  
  return(grow_fern_df)
}

# FUNCTION FOR PLOTING ANIMATED FERN WITH PLOTLY ###############################
grow_barnsley_fern = function(n_points = 3e4,
                              n_frames = 20,
                              point_size = 3,
                              point_color = ~ -y,
                              color_palette = 'Greens',
                              slider = TRUE) {
  fern_points = get_fern_points(0, 0, n = n_points)
  fern_points_animate = create_grow_df(fern_points, n_frames = n_frames)
  
  null_axis = list(
    title = '',
    zeroline = FALSE,
    showline = FALSE,
    showticklabels = FALSE,
    showgrid = FALSE
  )
  
  plotly::plot_ly(
    fern_points_animate,
    x =  ~ x,
    y =  ~ y,
    frame =  ~ Frame,
    type = 'scatter',
    mode = 'markers',
    colors = color_palette,
    color = point_color,
    marker = list(size = point_size),
    hoverinfo = "none",
    showlegend = FALSE
  ) %>%
    layout(xaxis = null_axis,
           yaxis = null_axis) %>%
    hide_colorbar() %>%
    animation_opts(frame=100, redraw = FALSE, transition=0) %>%
    animation_slider(hide = !slider) %>%
    config(displayModeBar = FALSE)
}

# DRAW FUNCTIONS EXAMPLE USAGE #################################################
draw_barnsley_fern()
grow_barnsley_fern()