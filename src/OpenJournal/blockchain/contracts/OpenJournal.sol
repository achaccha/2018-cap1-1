pragma solidity ^0.4.18;

import "./Token/JournalToken.sol";

contract OpenJournal is JournalToken {
    
    struct Journal {
        uint number;
        address author;
        string title;
        string description;     // 논문 해시값으로 대체해야 함
        uint value;
        uint[] subscribed;
        //uint[] reference_journal;
    }
    
    struct Subscriber {
        uint subscriber_number;             // 구독자 number(주소로 매칭시키기에는 무리가 있으므로)
        address subscriber_address;         // 구독자 주소
        uint[] subscriber_journal;          // 구독자가 구독한 리스트
    }    

    mapping (uint => Journal) public journals;                                  // 논문 번호 : Journal
    mapping (address => Subscriber) public subscribers;                         // 구독자 주소 : Subscriber
    mapping (address => mapping (uint => bool)) public is_subscribed;           // 구독자가 논문을 구독하였는지에 대한 여부

    uint public subscriberNumber = 2;       // Subscriber 번호(현재는 test 위해 2로 설정 해놓음)
    uint public journalNumber = 2;          // Journal 번호(현재는 test 위해 2로 설정 해놓음)
    uint public signUpCost = 100;           // 회원가입시 주어질 토큰
    uint public upperbound_value = 50;      // 저자가 논문 등록시 값의 상한선  
    address public master;    

    event LogSignUp(
        uint indexed _subscriber_number, 
        address indexed _subscriber_address, 
        uint[] _subscriber_journal
    );  

    event LogRegistJournal(
        uint indexed _number, 
        address indexed _author, 
        string _title, 
        uint _value
    );  

    event LogSubscribeJournal(
        address indexed _subscriber, 
        uint[] _myjournals, 
        uint[] _subscribed
    );     

    function signUp() public returns (bool) {
        subscriberNumber++;

        subscribers[msg.sender] = Subscriber(
            subscriberNumber,
            msg.sender,
            new uint[](0)
        );
        

        transferFrom(master, msg.sender, signUpCost);

        emit LogSignUp(subscriberNumber, msg.sender, subscribers[msg.sender].subscriber_journal);

    }

    function registJournal(uint _journalValue, string _title, string _description) public returns (bool) {
        require(_journalValue <= upperbound_value);
        journalNumber++;

        journals[journalNumber] = Journal(
            journalNumber,
            msg.sender,
            _title,
            _description,
            _journalValue,
            new uint[](0)            
        );

        emit LogRegistJournal(journalNumber, msg.sender, _title, _journalValue);       
    }

    function subscribeJournal(uint _journalNumber) public returns (bool){
        require(_journalNumber > 0 && _journalNumber <= journalNumber && is_subscribed[msg.sender][_journalNumber] == false);        

        transfer(journals[_journalNumber].author, journals[_journalNumber].value);
        uint sub_id = subscribers[msg.sender].subscriber_number;

        subscribers[msg.sender].subscriber_journal.push(_journalNumber);  
        journals[_journalNumber].subscribed.push(sub_id);       
        is_subscribed[msg.sender][_journalNumber] = true;

        emit LogSubscribeJournal(msg.sender, subscribers[msg.sender].subscriber_journal, journals[_journalNumber].subscribed);
    }

    function showSubscribedJournal() public view returns (uint[]){
        return subscribers[msg.sender].subscriber_journal;
    }

    function showJournalSubscriber(uint _journalNumber) public view returns (uint[]) {
        return journals[_journalNumber].subscribed;
    }
}
