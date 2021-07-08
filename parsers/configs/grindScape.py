parserConfig = {
    "firstParsing": {
        "separatorRegex": ":|;",
        "maxSplits": 3,
        "splitSettings": [
            {
                "splits": 1,
                "fields": [
                    "email",
                    "password"
                ]
            },
            {
                "splits": 2,
                "fields": [
                    "username",
                    "email",
                    "password"
                ]
            },
            {
                "splits": 3,
                "fields": [
                    "username",
                    "email",
                    "ip",
                    "password"
                ]
            }
        ],
    },
    "recursiveParsing": {
        "settings":  [
            {
                "fieldName": "email",
                "separatorRegex": "@",
                "maxSplits": 1,
                "splitSettings": [
                        {
                            "splits": 0,
                            "fields": [
                                "ignored"
                            ]
                        },
                        {
                            "splits": 1,
                            "fields": [
                                "emailLocal",
                                "emailDomain"
                            ]
                        }
                ]
            }
        ]
    },
    "outFields": [
        "username",
        "emailLocal",
        "emailDomain",
        "password"
    ]
}