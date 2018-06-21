#! /usr/bin/swift
import ScriptingBridge

@objc protocol iTunesTrack {
    @objc optional var artist: String{get}
    @objc optional var album: String {get}
}

@objc protocol iTunesApplication{
    @objc optional var currentTrack: iTunesTrack? {get}
}

extension SBApplication : iTunesApplication {}

let app: iTunesApplication = SBApplication(bundleIdentifier: "com.apple.iTunes")!

let currentTrack: iTunesTrack? = app.currentTrack!
let album = currentTrack?.album!
let artist = currentTrack?.artist!
print("\(album!)<\(artist!)")
