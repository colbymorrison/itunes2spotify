# iTunes2Spotify 

iTunes/Apple Music to Spotify library transfer tool. Add an album to your Spotify library by simply playing it in iTunes.

## Installation
`pip install itunes2spotify`

## Use
Login with your Spotify username:  
`i2s login` or provide username with `i2s login -u [USERNAME]`

Tranfer albums:  
`i2s transfer`

i2s will find the album on Spotify and ask for confirmation it is correct before adding, use `i2s transfer --no-interactive` to disable confirmation. If i2s is unsure it will display a list of potential matches, select the appropriate album. Not all albums on Apple Music and iTunes are avaiable on Spotify. 
