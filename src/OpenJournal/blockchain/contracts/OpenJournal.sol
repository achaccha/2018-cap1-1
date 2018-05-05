pragma solidity ^0.4.18;

import "./Token/JournalToken.sol";

contract OpenJournal is JournalToken(0, "JournalToken", 18, "jt") {
    
    struct Journal {
        uint256 number;
        address author;
        string title;
        string description;     // 논문 해시값으로 대체해야 함
        uint8 value;
        uint[] subscribed;
        //uint[] reference_journal;
    }
    
    struct Subscriber {
        uint256 subscriber_number;          // 구독자 number(주소로 매칭시키기에는 무리가 있으므로)
        address subscriber_address;         // 구독자 주소
        uint[] subscriber_journal;          // 구독자가 구독한 리스트
    }    

    mapping (uint => Journal) public journals;                                  // 논문 번호 : Journal
    mapping (address => Subscriber) public subscribers;                         // 구독자 주소 : Subscriber
    mapping (address => mapping (uint => bool)) public is_subscribed;           // 구독자가 논문을 구독하였는지에 대한 여부

    uint256 public subscriberNumber;       // Subscriber 번호(현재는 test 위해 2로 설정 해놓음)
    uint256 public journalNumber;          // Journal 번호(현재는 test 위해 2로 설정 해놓음)
    uint8 public signUpCost;               // 회원가입시 주어질 토큰
    uint8 public upperbound_value;         // 저자가 논문 등록시 값의 상한선  
    address public master;  // 임시로 설정  

    event LogSignUp(
    uint256 a,
    uint256 b,
        uint256 indexed _subscriber_number, 
        address indexed _subscriber_address, 
        uint[] _subscriber_journal
    );  

    event LogRegistJournal(
        uint256 indexed _number, 
        address indexed _author, 
        string _title, 
        uint8 _value
    );  

    event LogSubscribeJournal(
        address indexed _subscriber, 
        uint[] _myjournals, 
        uint[] _subscribed
    );

    event LogShowSubscribedJournal(
        uint[] _journals
    );  

    event LogShowJournalSubscriber(
        uint[] _subscriber
    );     

    function OpenJournal(
        uint256 _subscriberNumber,
        uint256 _journalNumber,
        uint8 _signUpCost,
        uint8 _upperbound_value
    ) public {
        subscriberNumber = _subscriberNumber;
        journalNumber = _journalNumber;
        signUpCost = _signUpCost;
        upperbound_value = _upperbound_value;
        master = msg.sender;
    }   

    function signUp(address _to) public returns (bool) {
        require(msg.sender == master);

        subscriberNumber++;            
        subscribers[_to] = Subscriber(
            subscriberNumber,
            _to,
            new uint[](0)
        );
        //transfer(_to, signUpCost);    왜 balances[msg.sender]가 0이되는걸까
        emit LogSignUp(balances[msg.sender], signUpCost, subscriberNumber, msg.sender, subscribers[msg.sender].subscriber_journal);

        return true;
    }

    function registJournal(uint8 _journalValue, string _title, string _description) public returns (bool) {
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

        return true;    
    }

    function subscribeJournal(uint256 _journalNumber) public returns (bool){
        require(_journalNumber > 0 && _journalNumber <= journalNumber && is_subscribed[msg.sender][_journalNumber] == false);        

        //transfer(journals[_journalNumber].author, journals[_journalNumber].value);
        uint sub_id = subscribers[msg.sender].subscriber_number;

        subscribers[msg.sender].subscriber_journal.push(_journalNumber);  
        journals[_journalNumber].subscribed.push(sub_id);       
        is_subscribed[msg.sender][_journalNumber] = true;

        emit LogSubscribeJournal(msg.sender, subscribers[msg.sender].subscriber_journal, journals[_journalNumber].subscribed);

        return true;
    }

    function showSubscribedJournal() public view returns (uint[]){
        emit LogShowSubscribedJournal(subscribers[msg.sender].subscriber_journal);

        return subscribers[msg.sender].subscriber_journal;
    }

    function showJournalSubscriber(uint _journalNumber) public view returns (uint[]) {
        emit LogShowJournalSubscriber(journals[_journalNumber].subscribed);

        return journals[_journalNumber].subscribed;
    }
}
