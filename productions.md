# Left Recursion Removal & Left Factorization

## Terms
- `Production` The rule as a whole
- `Non-Terminal Symbol` Symbols that are to be replaced
- `Terminal Symbol` Explicit symbol, such as a key word, value, or operator

## List of Non-Terminal Symbols
- [x] Rat16F
- [x] Opt Function Definitions
- [x] Opt Declaration List
- [x] Statement List
- [x] Function Definitions
- [x] Empty
- [x] Function
- [x] Identifier
- [x] Opt Parameter List
- [x] Body
- [x] Parameter List
- [x] Parameter
- [x] IDs
- [x] Qualifier
- [x] Statement List
- [x] Declaration List
- [x] Declaration
- [x] Statement
- [x] Compound
- [x] Assign
- [x] If
- [x] Return
- [x] Print
- [x] Scan
- [x] While
- [x] Expression
- [x] Condition
- [x] Return
- [x] Relop
- [x] Term
- [x] Factor
- [x] Primary
- [x] Integer
- [x] Real

## Left Recursion Removal
```
R1. <Rat19F>                     ::=        <Opt Function Definitions> %% <Opt Declaration List> <Statement List> %%
R2. <Opt Function Definitions>   ::=        <Function Definitions>   |   <Empty>
R3. <Function Definitions>       ::=        <Function>   |   <Function> <Function Definitions>   
R4. <Function>                   ::=        function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>
R5. <Opt Parameter List>         ::=        <Parameter List>   |   <Empty>
R6. <Parameter List>             ::=        <Parameter>   |   <Parameter> , <Parameter List>
R7. <Parameter>                  ::=        <IDs> <Qualifier> 
R8. <Qualifier>                  ::=        int   |   boolean   |   real 
R9. <Body>                       ::=        { <Statement List> }
R10. <Opt Declaration List>      ::=        <Declaration List>   |   <Empty>
R11. <Declaration List>          ::=        <Declaration> ;   |   <Declaration> ; <Declaration List>
R12. <Declaration>               ::=        <Qualifier> <IDs>                   
R13. <IDs>                       ::=        <Identifier>   |   <Identifier> , <IDs>
R14. <Statement List>            ::=        <Statement>   |   <Statement> <Statement List>
R15. <Statement>                 ::=        <Compound>   |   <Assign>   |   <If>   |   <Return>   |   <Print>   |   <Scan>   |   <While> 
R16. <Compound>                  ::=        { <Statement List> } 
R17. <Assign>                    ::=        <Identifier> = <Factor> <Term>' <Expression>' ;
R18. <If>                        ::=        if ( <Condition>  ) <Statement> fi   |   if ( <Condition> ) <Statement> otherwise <Statement> fi 
R19. <Return>                    ::=        return ; |  return <Factor> <Term>' <Expression>' ;
R20. <Print>                     ::=        put ( <Factor> <Term>' <Expression>' );
R21. <Scan>                      ::=        get ( <IDs> );
R22. <While>                     ::=        while ( <Condition>  ) <Statement>  
R23. <Condition>                 ::=        <Factor> <Term>' <Expression>' <Relop> <Factor> <Term>' <Expression>'
R24. <Relop>                     ::=        ==   |   /=   |   >   |   <   |   =>   |   <=        
R25. <Expression>                ::=        <Term> <Expression>'
R26. <Expression>'               ::=        + <Term> <Expression>'   |   - <Term> <Expression>'   |   epsilon
R27. <Term>                      ::=        <Factor> <Term>'
R28. <Term>'                     ::=        * <Factor> <Term>'   |   / <Factor> <Term>'   |   epsilon
R29. <Factor>                    ::=        - <Primary>   |   <Primary>
R30. <Primary>                   ::=        <Identifier>   |   <Integer>   |   <Identifier> ( <IDs> )   |   ( <Factor> <Term>' <Expression>' )   |   <Real>   |   true   |   false
R31. <Empty>                     ::=        epsilon
```

## Left Factorization
```
R1. <Rat19F>                     ::=        <Opt Function Definitions> %% <Opt Declaration List> <Statement List> %%
R2. <Opt Function Definitions>   ::=        <Function Definitions>   |   <Empty>
R3. <Function Definitions>       ::=        <Function> <Function Definitions>'
R4. <Function Definitions>'      ::=        <Empty>   |   <Function Definitions>
R5. <Function>                   ::=        function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>
R6. <Opt Parameter List>         ::=        <Parameter List>   |   <Empty>
R7. <Parameter List>             ::=        <Parameter> <Parameter List>'
R8. <Parameter List>'            ::=        <Empty> | , <Parameter List>
R9. <Parameter>                  ::=        <IDs> <Qualifier> 
R10. <Qualifier>                  ::=        int   |   boolean   |   real 
R11. <Body>                      ::=        { <Statement List> }
R12. <Opt Declaration List>      ::=        <Declaration List>   |   <Empty>
R13. <Declaration List>          ::=        <Declaration> ; <Declaration List>'
R14. <Declaration List>'         ::=        <Empty>   |   <Declaration List>
R15. <Declaration>               ::=        <Qualifier> <IDs>                   
R16. <IDs>                       ::=        <Identifier> <IDs>'
R17. <IDs>'                      ::=        <Empty>   |   , <IDs>
R18. <Statement List>            ::=        <Statement> <Statement List>'
R19. <Statement List>'           ::=        <Empty>   |   <Statement List>
R20. <Statement>                 ::=        <Compound>   |   <Assign>   |   <If>   |   <Return>   |   <Print>   |   <Scan>   |   <While> 
R21. <Compound>                  ::=        { <Statement List> } 
R22. <Assign>                    ::=        <Identifier> = <Factor> <Term>' <Expression>' ;
R23. <If>                        ::=        if ( <Condition>  ) <Statement> <If>'
R24. <If>'                       ::=        <fi>   |   otherwise <Statement> fi
R25. <Return>                    ::=        return <Return>'
R26. <Return>'                   ::=        ;   |   <Factor> <Term>' <Expression>' ;
R27. <Print>                     ::=        put ( <Factor> <Term>' <Expression>' );
R28. <Scan>                      ::=        get ( <IDs> );
R29. <While>                     ::=        while ( <Condition>  ) <Statement>  
R30. <Condition>                 ::=        <Factor> <Term>' <Expression>' <Relop> <Factor> <Term>' <Expression>'
R31. <Relop>                     ::=        ==   |   /=   |   >   |   <   |   =>   |   <=        
R32. <Expression>                ::=        <Term> <Expression>'
R33. <Expression>'               ::=        + <Term> <Expression>'   |   - <Term> <Expression>'   |   epsilon
R34. <Term>                      ::=        <Factor> <Term>'
R35. <Term>'                     ::=        * <Factor> <Term>'   |   / <Factor> <Term>'   |   epsilon
R36. <Factor>                    ::=        - <Primary>   |   <Primary>
R37. <Primary>                   ::=        <Identifier>   |   <Integer>   |   <Identifier> ( <IDs> )   |   ( <Factor> <Term>' <Expression>' )   |   <Real>   |   true   |   false
R38. <Empty>                     ::=        epsilon
```
