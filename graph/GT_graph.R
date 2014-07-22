#!/usr/bin/env Rscript

# GT_graph.R
# Copyright (C) 2014 Andrada, Vicente
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

library(ggplot2)
library(gridExtra)
library(gtools)

gt.file <- "~/Desktop/run2/GT.txt"
file.names <- "~/Desktop/run2/processed.txt"

# plots a single sample
plot.sample <- function(samp, par) {
  ggplot(na.omit(samp), aes_string(x=grep(par, colnames(samp), value=T))) +
    geom_bar() +
    labs(x="Genotype", y="Count", title=par) +
    stat_bin(geom="text", aes(label=..count..), vjust=0.10, hjust=0.0,
             size=3, colour="gray45") +
    theme(legend.position="none", text=element_text(size=6))
}

# plots multiple samples
# ** from Josh O'Brien at StackOverflow
# ** https://stackoverflow.com/questions/10706753/how-do-i-arrange-a-variable-list-of-plots-using-grid-arrange
make.plots <- function(df, name) {
  # sort colnames
  gs <- lapply(mixedsort(colnames(df)), FUN=function(x) plot.sample(df, x))
  n <- length(gs)
  nCol <- floor(sqrt(n))
  pdf(paste(name, "pdf", sep="."), width=11, height=8)
  do.call("grid.arrange", c(gs))
  dev.off()
}

# Read in the initial data
gt <- read.table(gt.file, header=TRUE, fill=TRUE, na.string="./.")
colnames(gt) <-
  c("Chromosome", "Position", readLines(file.names))

# create the data for each cell line
c10 <- gt[, grep("C10", names(gt), value=T)]
c258 <- gt[, grep("C258", names(gt), value=T)]
ews <- gt[, grep("EWS", names(gt), value=T)]
imr <- gt[, grep("IMR90", names(gt), value=T)]
t32 <- gt[, grep("T32", names(gt), value=T)]

# remove the initial data since it can be pretty big
rm(gt)

# graph the data
make.plots(c10, "C10")
make.plots(c258, "C258")
make.plots(ews, "EWS")
make.plots(imr, "IMR90")
make.plots(t32, "T32")
