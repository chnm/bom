---
title: "Analyzing the Arithmetic"
author: 
    - Jessica Otis
    - Jason Heppler
date: "2025-11-24"
tags: 
    - otis
    - heppler
    - data
categories: 
  - analysis
---

We are in the process of checking the arithmetic of the Bills of Mortality, both its internal consistency as well as the accuracy of our work, and are making our Jupyter notebooks of our analysis public. The notebooks take into account transcription errors, printing mistakes, illegible data, or duplicate data to capture a comprehensive analysis of the data.

[Checking for duplicate transcriptions](https://colab.research.google.com/drive/1QdV7PYJqNFbsY-SASZTYP0QeaX3ZkMtK?usp=sharing): This notebook analyzes duplicate transcriptions in the Bills of Mortality dataset to estimate the overall accuracy of our transcribed data. It does not differentiate between data that was mistranscribed and data that was printed differently in two separate copies of the same bill of mortality; both are considered "inaccurate" data.

[Mathematical accuracy of the general bills](https://colab.research.google.com/drive/1aqTvWX9dzDHir9pXe6r1fs_E4ZupCbyL?usp=sharing): This notebook analyzes transcriptions in the Bills of Mortality's general bills to estimate the overall accuracy of the general bill's mathematical accuracy. 

The following four notebooks all ask the same question, but handle the data in different ways: When we sum the total death counts from each parish (by plague and by all causes), how does that compare to the sum of the four subtotals calculated in the 17th/18th centuries and recorded in the Bills of Mortality? In other words, how accurate was the contemporary mathematics of the bills? 

- [Mathematical accuracy of the weekly bills data](https://colab.research.google.com/drive/1KIhDESXlpdtAZQ_vEg790uFD0TUMlWKN?usp=sharing): This version of the code uses original data without processing for duplicates or data marked illegible by transcribers.
- [Mathematical accuracy of the weekly bills data, data marked duplicated removed](https://colab.research.google.com/drive/1fMUbPC674ndtVYZhE33XPlo23rpTx5Y9?usp=sharing): This version of the code uses data processed for duplicates but not data marked illegible by transcribers.
- [Mathematical accuracy of the weekly bills data, data marked illegible removed](https://colab.research.google.com/drive/14f9I5eN9dfyIElUIb_0zXpTYt-tyxww9?usp=sharing): This version of the code uses data processed to exclude data marked illegible by transcribers but not duplicates.
- [Mathematical accuracy of the weekly bills data, duplicates and illegible data removed](https://colab.research.google.com/drive/1P8PcfvWSZKDLqD96d0Co3sIhtBUavGlA?usp=sharing): This version of the code uses data processed to exclude both duplicates and data marked illegible by transcribers.


