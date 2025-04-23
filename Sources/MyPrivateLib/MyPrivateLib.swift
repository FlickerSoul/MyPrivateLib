func mySecretFunction() -> Int {
    return Int.random(in: 1 ... 100)
}

public func myPublicFunction() -> Int {
    mySecretFunction()
}
