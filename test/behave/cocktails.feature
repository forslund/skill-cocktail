Feature: Cocktail functionality

  Scenario Outline: how do I mix a drink
    Given an english speaking user
     When the user says "how do I mix a <drink name>"
     Then mycroft reply should contain "<ingredient>"

  Examples: drink examples
    | drink name    | ingredient |
    | moscow mule   | lime juice |
    | gin and tonic | gin |

  @xfail
  Scenario Outline: Failing: how do I mix a drink
    Given an english speaking user
     When the user says "how do I mix a <drink name>"
     Then mycroft reply should contain "<ingredient>"

  Examples: drink examples
    | drink name    | ingredient |
    | margarita     | tequila |

  Scenario Outline: how do I make a drink
    Given an english speaking user
     When the user says "how do I make a <drink name>"
     Then mycroft reply should contain "<ingredient>"

  Examples: drink examples
    | drink name    | ingredient |
    | margarita     | tequila |
    | moscow mule   | lime juice |
    | gin and tonic | gin |

  Scenario Outline: how to make a drink
    Given an english speaking user
     When the user says "how to make a <drink name>"
     Then mycroft reply should contain "<ingredient>"

  Examples: drink examples
    | drink name           | ingredient |
    | old fashioned        | sugar |
    | long island iced tea | coca-cola |

  Scenario Outline: how to make a missing drink
    Given an english speaking user
     When the user says "how to make a <drink name>"
     Then "cocktails" should reply with dialog from "NotFound.dialog"

  Examples: drink examples
    | drink name         |
    | old fnord wrangler |
    | smashed fore-head  |
