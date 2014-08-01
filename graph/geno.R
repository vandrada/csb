# improved
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
#ggsave(file="t32_gt.pdf", width=11, height=4.25)
