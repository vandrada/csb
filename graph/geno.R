#!/usr/bin/env Rscript

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

library("ggplot2")
library("gtools")

melted <- read.table("~/Desktop/test/GT.txt", fill=TRUE, header=T,
                     na.strings=c('./.', '0/0'))

# set up the data frame
t32 <- melted[with(melted, grepl("T32", Sample)), ]
t32.olap <- t32[with(t32, grepl("olap", Sample)), ]
control <- t32[with(t32, grepl("0_accepted", Sample)), ]
t32.olap <- rbind(t32.olap, control)
t32.olap <- within(t32.olap, Sample <- factor(Sample, levels=mixedsort(Sample)))

# plot it
ggplot(data=na.omit(t32.olap), aes(x=Value)) + geom_bar() +
  facet_grid(. ~ Sample) + labs(x="Genotype", y="Count",
                                title="T32 Olaparib Genotype") +
  theme(text=element_text(size=8))
ggsave(file="t32_gt.pdf", width=11, height=4.25)
